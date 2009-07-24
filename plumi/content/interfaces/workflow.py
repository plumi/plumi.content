from zope.interface import Interface

class IPlumiWorkflow(Interface):
	""" Methods on objects that can under go checks internally before doing workflow transitions. """

	def autoPublishOrHide(self):
	    """Auto publish or hide"""

        def notifyOwnerVideoSubmitted(self):
	    """ Email the owner of the submitted video """

        def notifyReviewersVideoSubmitted(self):
	    """ Email the reviewers of the submitted video """

        def notifyOwnerVideoPublished(self):
	    """ Email the owner of the published video """
