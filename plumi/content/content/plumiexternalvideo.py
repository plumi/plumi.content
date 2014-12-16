"""
Definition of the Plumi External Video content type. This allows videos
from sites such as Vimeo and Youtube to be added as content.

Author:
  Sam Stainsby (sam@sustainablesoftware.com.au Sustainable Software Pty Ltd)
"""

from zope.interface import implements

try:
    from Products.LinguaPlone import atapi 
except ImportError:
    # No multilingual support
    from Products.Archetypes import atapi
from Products.ATContentTypes.content import base, schemata
from Products.Archetypes.interfaces import IMultiPageSchema
from Products.Archetypes.log import log

from plumi.content.config import PROJECTNAME
from plumi.content import plumiMessageFactory as _
from plumi.content.interfaces import IPlumiExternalVideo
from plumi.content.metadataextractor import extract

from plumivideo import PlumiVideoBaseSchema

import re


PlumiExternalVideoSchema = PlumiVideoBaseSchema.copy() + atapi.Schema((
    
    # # UPDATE: probably not needed now with use of collective.js.oembed.
    # #
    # # The Vimeo, Youtube, etc ID that can be used to construct the
    # # external URL and the code to embed the external player in 
    # # the page.
    # atapi.ComputedField(
    #     'ExternalID',
    #     storage=atapi.AnnotationStorage(),
    #     expression='context.parseExternalID()',
    #     widget=atapi.StringWidget(
    #         label=_(u"External Video ID"),
    #         description=_(u"The video ID from the external site.")
    #     ),
    #     languageIndependent=True,
    #     required=True,
    #     schemata='default',
    # )
))

# we need this to compute the external ID
PlumiExternalVideoSchema['WebsiteURL'].required = True
PlumiExternalVideoSchema['WebsiteURL'].widget.label = _(u"Video link")
PlumiExternalVideoSchema['WebsiteURL'].widget.description = _(u"The link to the video on the external site (on Vimeo, etc.).")
PlumiExternalVideoSchema.moveField('WebsiteURL', pos='top')

schemata.finalizeATCTSchema(PlumiExternalVideoSchema, moveDiscussion=False)


# urlPatterns = [
#   (
#     "YouTube",
#     r"^(https?://)?(www.)?youtube\.[a-z]{2,3}/watch/?\?v=(?P<id>[0-9a-z_]+)"
#   ),
#   (
#     "Vimeo",
#     r"^(https?://)?(www.)?vimeo\.[a-z]{2,3}/(?P<id>[0-9]+)"
#   )
# ]

class PlumiExternalVideo(base.ATCTContent):
    """Plumi External Video content"""
    implements(IPlumiExternalVideo, IMultiPageSchema)
    
    meta_type = "PlumiExternalVideo"
    schema = PlumiExternalVideoSchema
    
    # this is in PlumiVideoSchema, but causes recursion error here:
    #title = atapi.ATFieldProperty('title')
    #description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    thumbnailImageDescription = atapi.ATFieldProperty('thumbnailImageDescription')

    DateProduced = atapi.ATFieldProperty('DateProduced')

    FullDescription = atapi.ATFieldProperty('FullDescription')

    Distributor = atapi.ATFieldProperty('Distributor')

    WebsiteURL = atapi.ATFieldProperty('WebsiteURL')

    ProductionCompanyName = atapi.ATFieldProperty('ProductionCompanyName')

    ProjectName = atapi.ATFieldProperty('ProjectName')

    VideoLanguage = atapi.ATFieldProperty('VideoLanguage')

    ProducerMailingAddress = atapi.ATFieldProperty('ProducerMailingAddress')

    ProducerEmail = atapi.ATFieldProperty('ProducerEmail')

    Director = atapi.ATFieldProperty('Director')

    Producer = atapi.ATFieldProperty('Producer')

    thumbnailImage = atapi.ATFieldProperty('thumbnailImage')

    Countries = atapi.ATFieldProperty('Countries')

    Categories = atapi.ATFieldProperty('Categories')

    Genre = atapi.ATFieldProperty('Genre')

    #ExternalID = atapi.ATFieldProperty('ExternalID')
    
    # """Calculate the external ID from the WebsiteURL"""
    # def parseExternalID(self):
    #   externalUrl = self.getWebsiteURL()
    #   videoId = ''
    #   log('analysing video link: ' + repr(externalUrl))
    #   for pattern in urlPatterns:
    #     vendor = pattern[0]
    #     regex = pattern[1]
    #     log('  checking if this is a: ' + vendor + ' link')
    #     match = re.match(regex, externalUrl, re.I)
    #     if match:
    #       log('  this is a ' + repr(vendor) + ' video')
    #       videoId = match.group('id')
    #       log('    => ID: ' + repr(videoId))
    #       break
    #   return videoId


atapi.registerType(PlumiExternalVideo, PROJECTNAME)
