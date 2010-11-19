import sys
import logging
from zope.component import adapter
from zope.component import getUtility, queryUtility

from Acquisition import aq_parent
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from zope.component import getSiteManager
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.Archetypes.interfaces import IObjectInitializedEvent, IObjectEditedEvent
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from plone.registry.interfaces import IRegistry
from plone.app.discussion.interfaces import IDiscussionSettings
from zope.i18n import translate
from zope.i18nmessageid import Message

from plumi.content.interfaces.plumivideo import IPlumiVideo
from plumi.content.interfaces.workflow import IPlumiWorkflow
from plumi.content.metadataextractor import setup_metadata
from plumi.content import plumiMessageFactory as _
from collective.transcode.star.interfaces import ITranscodedEvent, ITranscodeTool
from plone.app.discussion.interfaces import IComment, ICommentingTool
from DateTime import DateTime
from urllib2 import urlopen
import socket
from PIL import Image


logger = logging.getLogger('plumi.content.subscribers')

try:
    # Plone 4:
    from Products.CMFCore.CMFCatalogAware import CatalogAware 
    PLONE_4 = True
except: # pragma: no cover
    # Plone 3:
    from OFS.Traversable import Traversable as CatalogAware
    PLONE_4 = False

MAIL_NOTIFICATION_MESSAGE = _(u"mail_notification_message",
    default=u"A comment with the title '${title}' "
             "has been posted here: ${link}")

@adapter(IPlumiVideo, ITranscodedEvent)
def notifyTranscodeSucceededPlumiVideo(obj, event):
    if event.profile == 'jpeg':
        imgfield = obj.getField('thumbnailImage') # check if there is already a thumbnail image
        if not imgfield or imgfield.getSize(obj) == (0, 0): # if not use the image returned by the transcoder
            try:
                tt = getUtility(ITranscodeTool)
                entry = tt[obj.UID()]['video_file'][event.profile]                
                url = '%s/%s' % (entry['address'], entry['path'])
                portal = getSiteManager()
                skins_tool = getToolByName(portal, 'portal_skins')
                defaultthumb = skins_tool['plumi_content_custom_images']['defaultthumb.jpeg']
                try:
                    logger.info("getting thumbnail from %s" % url)
                    socket.setdefaulttimeout(10)
                    f = urlopen(url)
                    #check if the file is actually a jpeg image else use a standard one
                    if f.headers['content-type'] == 'image/jpeg':
                        logger.info('setting thumbnail to %s' % entry['path'])
                        obj.setThumbnailImage(f.read())
                    else:
                        obj.setThumbnailImage(defaultthumb)
                    f.close()
                except:
                    logger.warn("Can't retrieve thumbnail from %s. Most likely due to a XML-RPC deadlock between Twisted and Plone." % url)
                    logger.warn("Plumi will now assume that the thumbnail is accessible through the filesystem in the transcoded directory to facilitate dev builds. If using in production you should always serve the transcoded videos through Apache")
                    try:
                        f = open(url[url.find('transcoded'):],'r')  
                        logger.info('setting thumbnail to %s' % entry['path'])                      
                        obj.setThumbnailImage(f.read())
                        f.close()
                    except:
                        obj.setThumbnailImage(defaultthumb)         
            except:
                logger.error("cannot set thumbnail for %s. Error %s" % (obj, sys.exc_info()[0]))


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
        log.info('notifyModifiedPlumiVideo: video replaced;')
        setup_metadata(obj)
        #setup_transcoding(obj)
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
    #setup_transcoding(obj)
    #THE END

@adapter(IPlumiVideo, IObjectInitializedEvent)
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
        mMsg += '\n\n' + _('A comment has been added on ') + videoUrl + '\n\n' 
        try:             
            portal.MailHost.send(mMsg.encode('utf-8', 'ignore'), mTo, mFrom, mSubj.encode('utf-8', 'ignore')) 
            log.info('notifyCommentAdded , im %s . sending email to %s from %s ' % (obj, mTo, mFrom) ) 
        except: 
            log.error('Didnt actually send email to contribution owner! Something amiss with SecureMailHost.') 

def notify_moderator(obj, event):
    """Tell the moderator when a comment needs attention.
    
       This method sends an email to the site admin (mail control panel setting)
       when a new comment has been added 
    """
    
    # Check if moderator notification is enabled
    registry = queryUtility(IRegistry)
    settings = registry.forInterface(IDiscussionSettings)
    if not settings.moderator_notification_enabled:
        return
    
    # Get informations that are necessary to send an email
    mail_host = getToolByName(obj, 'MailHost')
    portal_url = getToolByName(obj, 'portal_url')
    portal = portal_url.getPortalObject()
    sender = portal.getProperty('email_from_address')
    mto = portal.getProperty('email_from_address')
    
    # Check if a sender address is available
    if not sender:
        return

    conversation = aq_parent(obj)
    content_object = aq_parent(conversation)

    # Compose email        
    #comment = conversation.getComments().next()
    subject = translate(_(u"A comment has been posted."), context=obj.REQUEST)
    message = translate(Message(MAIL_NOTIFICATION_MESSAGE,
        mapping={'title': obj.title,
                 'link': content_object.absolute_url()}),
        context=obj.REQUEST)

    # Send email
    if PLONE_4:
        mail_host.send(message, mto, sender, subject, charset='utf-8')
    else:
        mail_host.secureSend(message, 
                             mto, 
                             sender, 
                             subject=subject, 
                             charset='utf-8') # pragma: no cover
