import sys
import logging
import socket
import datetime, pytz
from urllib2 import urlopen
from DateTime import DateTime
from PIL import Image

from Acquisition import aq_parent
from zope.app.component.hooks import getSite
from zope.component import getUtility, queryUtility
from Products.CMFCore.utils import getToolByName
from zope.component import getSiteManager
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.Archetypes.interfaces import IObjectInitializedEvent, IObjectEditedEvent
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from plone.registry.interfaces import IRegistry
from plone.app.discussion.interfaces import IDiscussionSettings
from zope.i18n import translate
from zope.i18nmessageid import Message
from zope.component import adapter
from zope.app.component.hooks import getSite

from plone.app.async.interfaces import IAsyncService
from Products.ATContentTypes.interfaces.image import IATImage
from Products.ATContentTypes.interfaces.event import IATEvent
from Products.ATContentTypes.interfaces.news import IATNewsItem
from plumi.content.interfaces.plumivideo import IPlumiVideo
from plumi.content.interfaces.plumicallout import IPlumiCallOut
from plumi.content.interfaces.workflow import IPlumiWorkflow
from plumi.content.adapters import sendMail
from plumi.content.metadataextractor import setup_metadata
from plumi.content import plumiMessageFactory as _
from collective.transcode.star.interfaces import ITranscodedEvent, ITranscodeTool
from plone.app.discussion.interfaces import IComment, ICommentingTool
from Products.CMFCore.WorkflowCore import WorkflowException
from plone.registry.interfaces import IRegistry

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
                async = getUtility(IAsyncService)
                temp_time = datetime.datetime.now(pytz.UTC) + datetime.timedelta(seconds=2)
                default = obj.portal_url() + '/defaultthumb.jpeg'
                job = async.queueJobWithDelay(None, temp_time, getThumbnail, obj, url, default)
                logger.info('getThumbail')
            except Exception as e:
                logger.error("cannot set thumbnail for %s. Error %s" % (obj, sys.exc_info()[0]))

def getThumbnail(obj, url, default):
    "get thumbnail from url"
    logger.info("getting thumbnail from %s" % url)
    portal = getSiteManager() 
    socket.setdefaulttimeout(10)
    try:
        f = urlopen(url)
        #check if the file is actually a jpeg image else use a standard one
        if f.headers['content-type'] == 'image/jpeg':
            logger.info('setting thumbnail to %s' % url)
            obj.setThumbnailImage(f.read())
            f.close()
        else:
            f.close()
            raise
    except:
        # set default thumb
        f = urlopen(default)
        obj.setThumbnailImage(f.read())
        f.close()


@adapter(IPlumiVideo, IActionSucceededEvent)
def notifyActionSucceededPlumiVideo(obj,event):
    """This gets called on IActionSucceededEvent - called whenever the object is transistioned thru workflow states."""
    workflow = getToolByName(obj,'portal_workflow')
    state = workflow.getInfoFor(obj,'review_state','')
    request = getSite().REQUEST 
    wf_action = request.get('workflow_action','')
    log = logging.getLogger('plumi.content.subscribers')
    log.info("notifyActionSuceededPlumiVideo... %s in state (%s) with event %s " % (obj.Title(), state,  event))
    registry = getUtility(IRegistry)

    #decide what to do , based on workflow of object
    #PUBLISHED
    log.info(state)
    if wf_action == 'retract':
        log.info('video retracted')
        if registry['plumi.content.browser.interfaces.IPlumiSettings.notifyReviewers']:     
            IPlumiWorkflow(obj).notifyOwnerVideoRetracted()
            IPlumiWorkflow(obj).notifyReviewersVideoRetracted()        
    elif wf_action == 'reject':
        log.info('video rejected')    
        if registry['plumi.content.browser.interfaces.IPlumiSettings.notifyReviewers']:
            IPlumiWorkflow(obj).notifyOwnerVideoRejected()
            IPlumiWorkflow(obj).notifyReviewersVideoRejected()
    elif state == 'pending' and not request.has_key('form.button.save'):
        log.info('video submitted for review')        
        if registry['plumi.content.browser.interfaces.IPlumiSettings.notifyReviewers']:
            IPlumiWorkflow(obj).notifyReviewersVideoSubmitted()
            IPlumiWorkflow(obj).notifyOwnerVideoSubmitted()
    elif state == 'published':
        log.info('doing published tasks')
        obj.reindexObject()
        
        #emails 
        IPlumiWorkflow(obj).notifyOwnerVideoPublished()

@adapter(IPlumiVideo, IObjectEditedEvent)
def notifyModifiedPlumiVideo(obj ,event):
    """This gets called on IObjectEditedEvent - called whenever the object is edited."""
    workflow = getToolByName(obj,'portal_workflow')
    state = workflow.getInfoFor(obj,'review_state','')
    log = logging.getLogger('plumi.content.subscribers')
    log.info("notifyModifiedPlumiVideo... %s in state (%s) with event %s " % (obj.Title(), state,  event))
    if getSite():
        request = getSite().REQUEST    
        #VISIBLE
        if state in ['private','visible'] and request.has_key('form.button.save'):
            #call IPlumiWorkflow API to decide if its ready to publish or needs hiding.
            # The adapter object will implement the logic for various content types
            if IPlumiWorkflow(obj).autoPublishOrHide():
                registry = getUtility(IRegistry)
                if registry['plumi.content.browser.interfaces.IPlumiSettings.notifyReviewers']:
                    IPlumiWorkflow(obj).notifyReviewersVideoSubmitted()
                    IPlumiWorkflow(obj).notifyOwnerVideoSubmitted()
        #PENDING , other states..
        if request.has_key('video_file_file'): #new video uploaded
            log.info('notifyModifiedPlumiVideo: video replaced;')
            async = getUtility(IAsyncService)
            temp_time = datetime.datetime.now(pytz.UTC) + datetime.timedelta(seconds=2)
            try: 
                job = async.queueJobWithDelay(None, temp_time, setup_metadata, obj)
                log.info("job queued: %s" % job)
            except Exception as e:
                log.error('failed to queue setup_metadata job: %s' % e)

@adapter(IPlumiVideo, IObjectInitializedEvent)
def notifyInitPlumiVideo(obj ,event):
    """This gets called on IObjectInitializedEvent - which occurs when a new object is created."""
    workflow = getToolByName(obj,'portal_workflow')
    state = workflow.getInfoFor(obj,'review_state','')
    log = logging.getLogger('plumi.content.subscribers')
    log.info("notifyInitPlumiVideo... %s in state (%s) with event %s " % (obj.Title(), state,  event))
    #create thumbnails for audio and image
    if 'image' in obj.getContentType() and not obj.getThumbnailImage():
        obj.setThumbnailImage(obj.video_file.data)
    elif 'audio' in obj.getContentType() and not obj.getThumbnailImage():
        image_path = getSite().absolute_url() + '/++resource++plumi.content.images/clip_default.png'
        f = urlopen(image_path)
        obj.setThumbnailImage(f.read())
        f.close()

    #decide what to do , based on workflow of object
    try:
        state = workflow.getInfoFor(obj,'review_state')
    except WorkflowException:
        log.info('failed to get workflow state for %s' % obj)            
        state = None
    request = getSite().REQUEST 
    #VISIBLE
    #works with the old and new publish video forms
    if state in ['private','visible'] and (request.has_key('form.button.save') or \
        request.form.has_key('form.buttons.apply')):
        #state in ['private','visible'] and request.['form.buttons.53617665206368616e676573']:
        #call IPlumiWorkflow API to decide if its ready to publish or needs hiding.
        # The adapter object will implement the logic for various content types
        if IPlumiWorkflow(obj).autoPublishOrHide():
            registry = getUtility(IRegistry)
            if registry['plumi.content.browser.interfaces.IPlumiSettings.notifyReviewers']:
                IPlumiWorkflow(obj).notifyOwnerVideoSubmitted()
                IPlumiWorkflow(obj).notifyReviewersVideoSubmitted()

    async = getUtility(IAsyncService)
    temp_time = datetime.datetime.now(pytz.UTC) + datetime.timedelta(seconds=2)
    try:
        job = async.queueJobWithDelay(None, temp_time, setup_metadata, obj)
        log.info("job queued: %s" % job)
    except Exception as e:
        log.error('failed to queue setup_metadata job: %s' % e)

def notifyInitItem(obj, event):
    """This gets called on IObjectInitializedEvent - called whenever the object is initialized."""
    workflow = getToolByName(obj,'portal_workflow')
    state = workflow.getInfoFor(obj,'review_state','')
    log = logging.getLogger('plumi.content.subscribers')
    log.info("notifyInitItem... %s in state (%s) with event %s " % (obj.Title(), state,  event))
    notify_reviewers(obj)

def autoSubmit(obj, event):
    """ Automatically submit news items, events & callouts """
    log = logging.getLogger('plumi.content.subscribers')    
    workflow = getToolByName(obj,'portal_workflow')
    try:
        state = workflow.getInfoFor(obj,'review_state')
        #dont try to resubmit if already published.
        if state == 'private':
           workflow.doActionFor(obj, 'show')
           log.info('autosubmit %s' % obj)
        if not state in ['published','pending']:
            workflow.doActionFor(obj, 'submit')
            log.info('autosubmit %s' % obj)
    except WorkflowException:
        log.info('failed to autosubmit %s' % obj)        

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
        try:
            mFrom = portal.getProperty('email_from_address') 
            mSubj = _('Comment added on: ') + video.Title().decode('utf-8') 
            mMsg = 'To: %s\n' % mTo
            mMsg += 'From: %s\n' % mFrom
            mMsg += 'Content-Type: text/plain; charset=utf-8\n\n'   
            mMsg = _('Hi ') + member.getProperty('fullname', creator) 
            mMsg += '\n\n' + _('A comment has been added on ') + videoUrl + '\n\n' 
            async = getUtility(IAsyncService)
            job = async.queueJobWithDelay(None, temp_time, sendMail, obj, mMsg, mSubj)
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
                context=obj.REQUEST,
                )

    # Send email
    if PLONE_4:
        mail_host.send(message, mto, sender, subject, charset='utf-8')
    else:
        mail_host.secureSend(message, 
                             mto, 
                             sender, 
                             subject=subject, 
                             charset='utf-8')


def notify_reviewers(obj):
    """Tell the reviewers when an item was submited.
    
       This method sends an email to the site admin (mail control panel setting)
       when a new object has been submitted
    """
    registry = getUtility(IRegistry)
    if registry['plumi.content.browser.interfaces.IPlumiSettings.notifyReviewers']:
        obj_title = obj.Title()
        obj_url= obj.absolute_url()
        creator = obj.Creator()
        membr_tool = getToolByName(getSite(),'portal_membership')
        member=membr_tool.getMemberById(creator)
        creator_info = {'fullname':member.getProperty('fullname', 'Fullname missing'),
                        'email':member.getProperty('email', None)}
        #search for reviewers 
        reviewers = membr_tool.searchForMembers(roles=['Reviewer'])
        for reviewer in reviewers:
            memberId = reviewer.id
            try:
                mTo = reviewer.getProperty('email', None)
                urltool = getToolByName(getSite(), 'portal_url')
                portal = urltool.getPortalObject()
                mFrom = portal.getProperty('email_from_address')
                mSubj = '%s -- submitted for your review' % obj_title
                mMsg = 'To: %s\n' % mTo
                mMsg += 'From: %s\n' % mFrom
                mMsg += 'Content-Type: text/plain; charset=utf-8\n\n'                    
                mMsg += _('Item has been submitted for your review').encode('utf-8','ignore') + '\n'
                mMsg += _('Please review the submitted content. ').encode('utf-8','ignore') + '\n\n'
                mMsg += 'Title: %s\n\n' % obj_title
                mMsg += '%s/view \n\n' % obj_url
                mMsg += 'The contributor was %s\n\n' % creator_info['fullname']
                mMsg += 'Email: %s\n\n' % creator_info['email']                    
                logger.info('notifyReviewersVideoSubmitted , im %s . sending email to %s from %s ' % (getSite(), mTo, mFrom) )
                async = getUtility(IAsyncService)
                job = async.queueJobWithDelay(None, temp_time, sendMail, obj, mMsg, mSubj)
            except Exception, e:
                logger.error('Didnt actually send email to reviewer! Something amiss with SecureMailHost. %s' % e)
