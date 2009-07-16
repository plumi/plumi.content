from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from plumi.content import contentMessageFactory as _

class IPlumiCallOut(Interface):
    """Call out for help with production of video content"""
    
    # -*- schema definition goes here -*-
    submissionCategories = schema.TextLine(
        title=_(u"Category"), 
        required=True,
        description=_(u"Categories. Hold down CTRL/COMMAND and click to multiple select topics."),
    )

    closingDate = schema.Date(
        title=_(u"Closing Date"), 
        required=True,
        description=_(u"Provide a date for when this callout will be closed."),
    )

