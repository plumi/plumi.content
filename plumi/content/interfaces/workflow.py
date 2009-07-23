from zope.interface import Interface

class IPlumiWorkflow(Interface):
	""" Methods on objects that can under go checks internally before doing workflow transitions. """

	def autoPublishOrHide(self):
	    """Auto publish or hide"""
