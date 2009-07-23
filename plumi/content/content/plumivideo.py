"""Definition of the Plumi Video content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.Archetypes.interfaces import IMultiPageSchema

#third party products
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.ATCountryWidget.Widget import CountryWidget
from plone.app.blob.field import BlobField, BlobMarshaller
# plumi.content imports
from plumi.content import contentMessageFactory as _
from plumi.content.interfaces import IPlumiVideo
from plumi.content.config import PROJECTNAME

PlumiVideoSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.StringField(
        'thumbnailImageDescription',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Thumbnail Image description"),
            description=_(u"The caption for the thumbnail image."),
        ),
	#schemata='Video',
    ),


    atapi.DateTimeField(
        'DateProduced',
        storage=atapi.AnnotationStorage(),
        widget=atapi.CalendarWidget(
            label=_(u"Date Produced"),
            description=_(u"The date the video content was released."),
        ),
        validators=('isValidDate'),
    ),


    atapi.TextField(
        'FullDescription',
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Full Description"),
            description=_(u"The description of the video content"),
        ),
    ),


    atapi.StringField(
        'Distributor',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Distributor"),
            description=_(u"The Distributor of the video content"),
        ),
    ),


    atapi.StringField(
        'WebsiteURL',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Website URL"),
            description=_(u"The website URL for the video content"),
        ),
    ),


    atapi.StringField(
        'ProductionCompanyName',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Production Company Name"),
            description=_(u"Production Company Name"),
        ),
    ),


    atapi.StringField(
        'ProjectName',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Project Name"),
            description=_(u"Project Name"),
        ),
    ),


    atapi.StringField(
        'ProducerMailingAddress',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Producer Mailing Address"),
            description=_(u"The Producer's mailing address"),
        ),
    ),


    atapi.StringField(
        'ProducerEmail',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Producer Email Address"),
            description=_(u"The Producer's email address"),
        ),
        validators=('isEmail'),
    ),


    atapi.StringField(
        'Director',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Director"),
            description=_(u"The Director of the video content"),
        ),
    ),


    atapi.StringField(
        'Producer',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Producer"),
            description=_(u"The Producer of the video content"),
        ),
    ),


    atapi.ImageField(
        'thumbnailImage',
        storage=atapi.AnnotationStorage(),
        widget=atapi.ImageWidget(
            label=_(u"Video Thumbnail"),
            description=_(u"The thumbnail image for the video content"),
        ),
        validators=('isNonEmptyFile'),
	#schemata='Video',

    ),


    atapi.StringField(
        'Countries',
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
	#schemata='Video',

    ),


))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

PlumiVideoSchema['title'].storage = atapi.AnnotationStorage()
PlumiVideoSchema['description'].storage = atapi.AnnotationStorage()

PlumiVideoSchema.changeSchemataForField('DateProduced', 'dates')

PlumiVideoSchema.changeSchemataForField('Genre', 'categorization')
PlumiVideoSchema.changeSchemataForField('Distributor', 'categorization')
PlumiVideoSchema.changeSchemataForField('WebsiteURL', 'categorization')
PlumiVideoSchema.changeSchemataForField('ProductionCompanyName', 'categorization')
PlumiVideoSchema.changeSchemataForField('ProjectName', 'categorization')
PlumiVideoSchema.changeSchemataForField('ProducerMailingAddress', 'categorization')
PlumiVideoSchema.changeSchemataForField('ProducerEmail', 'categorization')
PlumiVideoSchema.changeSchemataForField('Director', 'categorization')
PlumiVideoSchema.changeSchemataForField('Producer', 'categorization')
PlumiVideoSchema.changeSchemataForField('Countries', 'categorization')
PlumiVideoSchema.changeSchemataForField('Categories', 'categorization')



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
    thumbnailImageDescription = atapi.ATFieldProperty('thumbnailImageDescription')

    DateProduced = atapi.ATFieldProperty('DateProduced')

    FullDescription = atapi.ATFieldProperty('FullDescription')

    Distributor = atapi.ATFieldProperty('Distributor')

    WebsiteURL = atapi.ATFieldProperty('WebsiteURL')

    ProductionCompanyName = atapi.ATFieldProperty('ProductionCompanyName')

    ProjectName = atapi.ATFieldProperty('ProjectName')

    ProducerMailingAddress = atapi.ATFieldProperty('ProducerMailingAddress')

    ProducerEmail = atapi.ATFieldProperty('ProducerEmail')

    Director = atapi.ATFieldProperty('Director')

    Producer = atapi.ATFieldProperty('Producer')

    thumbnailImage = atapi.ATFieldProperty('thumbnailImage')

    Countries = atapi.ATFieldProperty('Countries')

    Categories = atapi.ATFieldProperty('Categories')

    Genre = atapi.ATFieldProperty('Genre')

    video_file = atapi.ATFieldProperty('video_file')


atapi.registerType(PlumiVideo, PROJECTNAME)
