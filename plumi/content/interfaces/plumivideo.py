from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from plumi.content import contentMessageFactory as _

class IPlumiVideo(Interface):
    """Plumi Video content"""
    
    # -*- schema definition goes here -*-
    Country = schema.TextLine(
        title=_(u"Country of origin of the video"), 
        required=False,
        description=_(u"The associated country of origin of the video content"),
    )

    Categories = schema.List(
        title=_(u"Video Categories"), 
        required=False,
        description=_(u"The video categories - select as many as applicable."),
    )

    Genre = schema.TextLine(
        title=_(u"Video Genre"), 
        required=False,
        description=_(u"The genre of the video"),
    )

    video_file = schema.Bytes(
        title=_(u"Video File"), 
        required=True,
        description=_(u"The uploaded video file"),
    )

