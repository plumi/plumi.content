from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from plumi.content import plumiMessageFactory as _

class IPlumiVideo(Interface):
    """Plumi Video content"""
    
    # -*- schema definition goes here -*-
    thumbnailImageDescription = schema.TextLine(
        title=_(u"Thumbnail Image description"), 
        required=False,
        description=_(u"The caption for the thumbnail image."),
    )

    DateProduced = schema.Date(
        title=_(u"Date Produced"), 
        required=False,
        description=_(u"The date the video content was released."),
    )

    FullDescription = schema.Text(
        title=_(u"Full Description"), 
        required=False,
        description=_(u"The description of the video content"),
    )

    Distributor = schema.TextLine(
        title=_(u"Distributor"), 
        required=False,
        description=_(u"The Distributor of the video content"),
    )

    WebsiteURL = schema.TextLine(
        title=_(u"Website URL"), 
        required=False,
        description=_(u"The website URL for the video content"),
    )

    ProductionCompanyName = schema.TextLine(
        title=_(u"Production Company Name"), 
        required=False,
        description=_(u"Production Company Name"),
    )

    ProjectName = schema.TextLine(
        title=_(u"Project Name"), 
        required=False,
        description=_(u"Project Name"),
    )

    ProducerMailingAddress = schema.TextLine(
        title=_(u"Producer Mailing Address"), 
        required=False,
        description=_(u"The Producer's mailing address"),
    )

    ProducerEmail = schema.TextLine(
        title=_(u"Producer Email Address"), 
        required=False,
        description=_(u"The Producer's email address"),
    )

    Director = schema.TextLine(
        title=_(u"Director"), 
        required=False,
        description=_(u"The Director of the video content"),
    )

    Producer = schema.TextLine(
        title=_(u"Producer"), 
        required=False,
        description=_(u"The Producer of the video content"),
    )

    thumbnailImage = schema.Bytes(
        title=_(u"Video Thumbnail"), 
        required=False,
        description=_(u"The thumbnail image for the video content"),
    )

    Countries = schema.TextLine(
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

class ICallBackView(Interface):
    """
    """
    def conv_done_xmlrpc(status, message, profile, path):
        """
        """
