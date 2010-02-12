import logging
from zope.component import adapter
from zope.component import getUtility

from Acquisition import aq_parent
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IActionSucceededEvent
#from zope.app.container.interfaces import IObjectModifiedEvent
from Products.Archetypes.interfaces import IObjectInitializedEvent, IObjectEditedEvent

from plumi.content.interfaces.plumivideo import IPlumiVideo
from plumi.content.interfaces.workflow import IPlumiWorkflow
from plumi.content.transcoding import setup_transcoding
from plumi.content.metadataextractor import setup_metadata
from plumi.content import plumiMessageFactory as _

#from vaporisation.vaporisation.events import TreeUpdateEvent

@adapter(IPlumiVideo, IActionSucceededEvent)
def notifyActionSucceededPlumiVideo(obj,event):
    """This gets called on IActionSucceededEvent - called whenever the object is transistioned thru workflow states."""
    workflow = getToolByName(obj,'portal_workflow')
    state = workflow.getInfoFor(obj,'review_state','')
    request = getSite().REQUEST 
    wf_action = request.get('workflow_action','')
    log = logging.getLogger('plumi.content.subscribers')
    log.info("notifyActionSuceededPlumiVideo... %s in state (%s) with event %s " % (obj.Title(), state,  event))
    #decide what to do , based on workflow of object
    #PUBLISHED
    log.info(state)
    if wf_action == 'retract':
        log.info('video retracted')
        IPlumiWorkflow(obj).notifyOwnerVideoRetracted()
        IPlumiWorkflow(obj).notifyReviewersVideoRetracted()        
    elif wf_action == 'reject':
        log.info('video rejected')    
        IPlumiWorkflow(obj).notifyOwnerVideoRejected()
        IPlumiWorkflow(obj).notifyReviewersVideoRejected()
    elif state == 'pending' and not request.has_key('form.button.save'):
        log.info('video submitted for review')        
        IPlumiWorkflow(obj).notifyReviewersVideoSubmitted()
        IPlumiWorkflow(obj).notifyOwnerVideoSubmitted()
    elif state == 'published':
        log.info('doing published tasks')

        obj.reindexObject()

        #refresh the catalog
        #XXX make it configurable to run a catalog refresh each time , or not?
        #portal_catalog = getToolByName(obj,'portal_catalog')
        #portal_catalog.refreshCatalog()

        #update the tag cloud
        portal_url = getToolByName(obj, "portal_url")
        portal = portal_url.getPortalObject()
        tc = getattr(portal,'tagcloud',None)
        if tc is not None:
            log.info('FIXME - refresh tag cloud!')
            # XXX re-implement vaporisation compatibility
            #notify(TreeUpdateEvent(tc))
        #emails 
        IPlumiWorkflow(obj).notifyOwnerVideoPublished()

@adapter(IPlumiVideo, IObjectEditedEvent)
def notifyModifiedPlumiVideo(obj ,event):
    """This gets called on IObjectEditedEvent - called whenever the object is edited."""
    workflow = getToolByName(obj,'portal_workflow')
    state = workflow.getInfoFor(obj,'review_state','')
    log = logging.getLogger('plumi.content.subscribers')
    log.info("notifyModifiedPlumiVideo... %s in state (%s) with event %s " % (obj.Title(), state,  event))
    request = getSite().REQUEST    
    #VISIBLE
    if state == 'visible' and request.has_key('form.button.save'):
        #call IPlumiWorkflow API to decide if its ready to publish or needs hiding.
        # The adapter object will implement the logic for various content types
        if IPlumiWorkflow(obj).autoPublishOrHide():
            IPlumiWorkflow(obj).notifyReviewersVideoSubmitted()
            IPlumiWorkflow(obj).notifyOwnerVideoSubmitted()
    #PENDING , other states..
    if request.has_key('video_file_file'): #new video uploaded
        log.info('notifyModifiedPlumiVideo: video replaced; retranscoding')
        setup_metadata(obj)
        setup_transcoding(obj)
    #THE END

@adapter(IPlumiVideo, IObjectInitializedEvent)
def notifyInitPlumiVideo(obj ,event):
    """This gets called on IObjectInitializedEvent - which occurs when a new object is created."""
    workflow = getToolByName(obj,'portal_workflow')
    state = workflow.getInfoFor(obj,'review_state','')
    log = logging.getLogger('plumi.content.subscribers')
    log.info("notifyInitPlumiVideo... %s in state (%s) with event %s " % (obj.Title(), state,  event))
    #decide what to do , based on workflow of object
    state = workflow.getInfoFor(obj,'review_state')
    request = getSite().REQUEST    
    #VISIBLE
    if state == 'visible' and request.has_key('form.button.save'):
        #call IPlumiWorkflow API to decide if its ready to publish or needs hiding.
        # The adapter object will implement the logic for various content types
        if IPlumiWorkflow(obj).autoPublishOrHide():
            IPlumiWorkflow(obj).notifyOwnerVideoSubmitted()
            IPlumiWorkflow(obj).notifyReviewersVideoSubmitted()

    setup_metadata(obj)
    setup_transcoding(obj)
    #THE END

def autoSubmit(obj, event):
    """ Automatically submit news items, events & callouts """
    log = logging.getLogger('plumi.content.subscribers')    
    workflow = getToolByName(obj,'portal_workflow')
    try:
        state = workflow.getInfoFor(obj,'review_state')
        #dont try to resubmit if already published.
        if not state in ['published','pending']:
            workflow.doActionFor(obj, 'submit')
            log.info('autosubmit %s' % obj)
        worked = True
    except WorkflowException:
        worked = False
        log.info('failed to autosubmit %s' % obj)        
        pass
                        
def notifyCommentAdded(obj ,event):
    """Notify owner of added comment"""
    log = logging.getLogger('plumi.content.subscribers')
    urltool = getToolByName(obj, 'portal_url')
    portal = urltool.getPortalObject()
    video = aq_parent(aq_parent(obj))
    videoUrl = video.absolute_url()
    
    creator= video.Creator()
    membr_tool = getToolByName(obj,'portal_membership')
    member=membr_tool.getMemberById(creator)
    mTo = member.getProperty('email',None)
    log.info('notifyCommentAdded')
    if mTo:
        mFrom = portal.getProperty('email_from_address')
        mSubj = _('Comment added on: ') + video.Title().decode('utf-8')
        mMsg = _('Hi ') + member.getProperty('fullname', creator)
        mMsg += _('\n\n A comment has been added on ') + videoUrl + '\n\n'
        try:            
	    portal.MailHost.send(mMsg.encode('utf-8', 'ignore'), mTo, mFrom, mSubj.encode('utf-8', 'ignore'))
            log.info('notifyCommentAdded , im %s . sending email to %s from %s ' % (obj, mTo, mFrom) )
        except:
	    log.error('Didnt actually send email to contribution owner! Something amiss with SecureMailHost.')

