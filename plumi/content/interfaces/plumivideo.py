from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from plumi.content import contentMessageFactory as _

class IPlumiVideo(Interface):
    """Plumi Video conent"""
    
    # -*- schema definition goes here -*-
    video_file = schema.Bytes(
        title=_(u"Video File"), 
        required=True,
        description=_(u"The uploaded video file"),
    )

