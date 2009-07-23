import logging
from zope.component import adapter
from zope.event import notify
from zope.app.event.objectevent import ObjectModifiedEvent
from zope.app.container.interfaces import IObjectModifiedEvent

from Products.CMFCore.WorkflowCore import WorkflowException

from Products.CMFCore.utils import getToolByName

from plumi.content.interfaces.plumivideo import IPlumiVideo
from plumi.content.interfaces.workflow import IPlumiWorkflow

#from vaporisation.vaporisation.events import TreeUpdateEvent

@adapter(IPlumiVideo, IObjectModifiedEvent)
def notifyModifiedPlumiVideo(obj ,event):
    """This gets called on IObjectModifiedEvent"""
    workflow = getToolByName(obj,'portal_workflow')
    state = workflow.getInfoFor(obj,'review_state','')
    log = logging.getLogger('plumi.content')
    log.info("notifyModifiedPlumiVideo... %s in state (%s) with event %s " % (obj.Title(), state,  event))
    state = workflow.getInfoFor(obj,'review_state')
    if state == 'published':
	log.info('doing published tasks')
	#refresh the catalog
	#XXX make it configurable?
        portal_catalog = getToolByName(obj,'portal_catalog')
        portal_catalog.refreshCatalog()
	#update the tag cloud
	portal_url = getToolByName(obj, "portal_url")
        portal = portal_url.getPortalObject()
	tc = getattr(portal,'tagcloud',None)
	if tc is not None:
	    log.info('FIXME - refresh tag cloud!')
	    # XXX vaporisation compatibility
	    #notify(TreeUpdateEvent(tc))
    if state == 'visible':
	#call IPlumiWorkflow API to decide if its ready to publish or needs hiding.
	IPlumiWorkflow(obj).autoPublishOrHide()
