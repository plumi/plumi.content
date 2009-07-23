import logging
from zope.component import adapts
from zope.interface import implements
from interfaces.plumivideo import IPlumiVideo
from interfaces.workflow import IPlumiWorkflow

class PlumiWorkflowAdapter(object):
    implements(IPlumiWorkflow)
    adapts(IPlumiVideo)

    def __init__(self, context):
	self.context = context

    def autoPublishOrHide(self):
	""" Implement auto publish or hide functionality """
	logger = logging.getLogger('plumi.content.adapaters')
	
	logger.info('autoPublishOrHide , im %s ' % self.context )
