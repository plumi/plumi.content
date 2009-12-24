import logging
from zope.component import adapter
from zope.component import getUtility
from zope.annotation.interfaces import IAnnotations
from Products.CMFCore.utils import getToolByName

from Products.CMFCore.interfaces import IActionSucceededEvent
#from zope.app.container.interfaces import IObjectModifiedEvent
from Products.Archetypes.interfaces import IObjectInitializedEvent, IObjectEditedEvent
from Products.CMFCore.interfaces import IPropertiesTool

from plumi.content.interfaces.plumivideo import IPlumiVideo
from plumi.content.interfaces.workflow import IPlumiWorkflow

#from vaporisation.vaporisation.events import TreeUpdateEvent

import transaction
from ZODB.PersistentMapping import PersistentMapping
import xmlrpclib
import urllib
from urlparse import urlparse

@adapter(IPlumiVideo, IActionSucceededEvent)
def notifyActionSucceededPlumiVideo(obj,event):
    """This gets called on IActionSucceededEvent - called whenever the object is transistioned thru workflow states."""
    workflow = getToolByName(obj,'portal_workflow')
    state = workflow.getInfoFor(obj,'review_state','')
    log = logging.getLogger('plumi.content.subscribers')
    log.info("notifyActionSuceededPlumiVideo... %s in state (%s) with event %s " % (obj.Title(), state,  event))
    #decide what to do , based on workflow of object
    state = workflow.getInfoFor(obj,'review_state')
    #PUBLISHED
    if state == 'published':
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
    #VISIBLE
    if state == 'visible':
	#call IPlumiWorkflow API to decide if its ready to publish or needs hiding.
	# The adapter object will implement the logic for various content types
	if IPlumiWorkflow(obj).autoPublishOrHide():
	    IPlumiWorkflow(obj).notifyReviewersVideoSubmitted()
	    IPlumiWorkflow(obj).notifyOwnerVideoSubmitted()
    setup_transcoding(obj)
    #PENDING , other states..

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
    #VISIBLE
    if state == 'visible':
	#call IPlumiWorkflow API to decide if its ready to publish or needs hiding.
	# The adapter object will implement the logic for various content types
	if IPlumiWorkflow(obj).autoPublishOrHide():
		IPlumiWorkflow(obj).notifyOwnerVideoSubmitted()
		IPlumiWorkflow(obj).notifyReviewersVideoSubmitted()

    setup_transcoding(obj)
    #THE END

def setup_transcoding(obj):
    annotations = IAnnotations(obj, None)
    if not annotations.has_key('plumi.transcode.profiles'):
        annotations['plumi.transcode.profiles'] = PersistentMapping()

    pprop = getUtility(IPropertiesTool)
    config = getattr(pprop, 'plumi_properties', None)
    #TODO Check if we have transcoding support enabled
    try:
        transcodeServer=xmlrpclib.ServerProxy(config.transcodedaemon_address)
        transcodeProfiles = transcodeServer.getAvailableProfiles()
    except Exception, e:
        print 'ERROR: Could not connect to transcode daemon %s: %s' % (config.transcodedaemon_address, e)
        return
    #Submit XML-RPC call to transcoder
    transcodeOptions = dict()
    
    #TODO - get better way of discovering the path to the video file
    path = obj.absolute_url_path()
    if config.plonesite_address:
        plonesite = urlparse(config.plonesite_address)
    else:
        plonesite = urlparse(obj.absolute_url())
    url_format = "%s://%s:%s@%s%s/@@streaming_RPC"

    cb_url = url_format % ( plonesite[0], #protocol
                            config.plonesite_login,
                            config.plonesite_password,
                            plonesite[1], #netloc
                            urllib.quote(path)) #path (for this video)
                           
    transcodeInput=dict(path = ( plonesite[0] + "://" + 
                                 plonesite[1] + path + 
                                 '/download/video_file/' + 
                                 obj.video_file.getFilename()), 
                        type=obj.video_file.getContentType())

    trans = transaction.get()
    for transcodeProfile in transcodeProfiles:
        print "plumi running profile %s" % transcodeProfile

        trans.addAfterCommitHook(launchConversion, 
                                (transcodeServer, transcodeInput, 
                                transcodeProfile, transcodeOptions, cb_url))
    
    #self.info ['state'] = "processing"

    print "plumi: ConvertDaemon call pending"

def launchConversion(status, server, input, profile, options, cb_url):
    """
    """
    if not status:
        return
    try:
        jobId = server.convert(input, profile, options, cb_url)
        print "plumi: ConvertDaemon call "+jobId
    #except xmlrpclib.Error, e:
    except Exception, e:
        print "plumi: ConvertDaemon call FAILED", e
        server=xmlrpclib.ServerProxy(cb_url)
        server.conv_done_xmlrpc(e)
    #print "INPUT ", input_path
    #print "OUTPUT", output_path
    #return jobId
