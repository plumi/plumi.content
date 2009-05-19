"""Definition of the Plumi Video content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.ATCountryWidget.Widget import CountryWidget

from plone.app.blob.field import BlobField, BlobMarshaller

from plumi.content import contentMessageFactory as _
from plumi.content.interfaces import IPlumiVideo
from plumi.content.config import PROJECTNAME

PlumiVideoSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.StringField(
        'Country',
        storage=atapi.AnnotationStorage(),
        widget=CountryWidget(
            label=_(u"Country of origin of the video"),
            description=_(u"The associated country of origin of the video content"),
        ),
    ),


    atapi.LinesField(
        'Categories',
        storage=atapi.AnnotationStorage(),
        widget=atapi.MultiSelectionWidget(
            label=_(u"Video Categories"),
            description=_(u"The video categories - select as many as applicable."),
        ),
        vocabulary=NamedVocabulary("""video_categories"""),

    ),


    atapi.StringField(
        'Genre',
        storage=atapi.AnnotationStorage(),
        widget=atapi.SelectionWidget(
            label=_(u"Video Genre"),
            description=_(u"The genre of the video"),
        ),
        vocabulary=NamedVocabulary("""video_genre"""),
    ),


    BlobField(
        'video_file',
	storage=atapi.AnnotationStorage(), 
	primary=True,
        required=True,
	accessor='getFile',
	mutator='setFile',
        widget=atapi.FileWidget(
            label=_(u"Video File"),
            description=_(u"The uploaded video file"),
        ),
        validators=('isNonEmptyFile'),
    ),


))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

PlumiVideoSchema['title'].storage = atapi.AnnotationStorage()
PlumiVideoSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(PlumiVideoSchema, moveDiscussion=False)
PlumiVideoSchema.registerLayer('marshall', BlobMarshaller())

class PlumiVideo(base.ATCTContent):
    """Plumi Video content"""
    implements(IPlumiVideo)

    meta_type = "PlumiVideo"
    schema = PlumiVideoSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    Country = atapi.ATFieldProperty('Country')

    Categories = atapi.ATFieldProperty('Categories')

    Genre = atapi.ATFieldProperty('Genre')

    video_file = atapi.ATFieldProperty('video_file')


atapi.registerType(PlumiVideo, PROJECTNAME)
