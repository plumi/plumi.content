import logging
from zope.component import adapter
from Products.CMFCore.utils import getToolByName

from Products.CMFCore.interfaces import IActionSucceededEvent
#from zope.app.container.interfaces import IObjectModifiedEvent
from Products.Archetypes.interfaces import IObjectInitializedEvent, IObjectEditedEvent

from plumi.content.interfaces.plumivideo import IPlumiVideo
from plumi.content.interfaces.workflow import IPlumiWorkflow

#from vaporisation.vaporisation.events import TreeUpdateEvent


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

    #THE END
