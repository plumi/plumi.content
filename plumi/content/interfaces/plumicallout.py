from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from plumi.content import contentMessageFactory as _

class IPlumiCallOut(Interface):
    """Call out for help with production of video content"""
    
    # -*- schema definition goes here -*-
    websiteURL = schema.TextLine(
        title=_(u"Website Address"), 
        required=False,
        description=_(u"Website for more info about the callout"),
    )

    calloutImageCaption = schema.TextLine(
        title=_(u"Image caption"), 
        required=True,
        description=_(u"The text caption describing the image"),
    )

    calloutImage = schema.Bytes(
        title=_(u"Image"), 
        required=True,
        description=_(u"Will be shown in the call out listings, and the call out item itself. Image will be scaled to a sensible size."),
    )

    bodyText = schema.Text(
        title=_(u"Body Text"), 
        required=True,
        description=_(u"The main text content"),
    )

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

