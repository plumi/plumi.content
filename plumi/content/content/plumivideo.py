"""Definition of the Plumi Video content type
"""

from zope.interface import implements, directlyProvides

try:
    from Products.LinguaPlone import atapi 
except ImportError:
    # No multilingual support
    from Products.Archetypes import atapi

from Products.Archetypes.interfaces import IMultiPageSchema
from Products.ATContentTypes.content import base,schemata
from Products.ATContentTypes.configuration import zconf

#third party products
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.ATCountryWidget.Widget import CountryWidget
from plone.app.blob.field import BlobField, BlobMarshaller
# plumi.content imports
from plumi.content import plumiMessageFactory as _
from plumi.content.interfaces import IPlumiVideo
from plumi.content.config import PROJECTNAME
from plumi.content.metadataextractor import extract
from zope.app.component.hooks import getSite

PlumiVideoSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.StringField(
        'Producer',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Producer"),

        ),
        languageIndependent=True,
        schemata='default',        
    ),

    atapi.StringField(
        'Director',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Director"),
        ),
        languageIndependent=True,
        schemata='default',        
    ),
    
    atapi.StringField(
        'ProducerEmail',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Producer Email Address"),
        ),
        validators=('isEmail'),
        languageIndependent=True,
        schemata='default',        
    ),

    atapi.StringField(
        'ProducerMailingAddress',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Producer Mailing Address"),
        ),
        languageIndependent=True,
        schemata='default',        
    ),
        
    atapi.StringField(
        'ProjectName',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Project Name"),
        ),
        schemata='default',                
    ),
    
    atapi.StringField(
        'ProductionCompanyName',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Production Company Name"),
        ),
        schemata='default',                
    ),


    atapi.StringField(
        'WebsiteURL',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Website URL"),
        ),
        languageIndependent=True,
        schemata='default',        
    ),

    atapi.StringField(
        'Distributor',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Distributor"),
        ),
        schemata='default',                
    ),
    
    atapi.DateTimeField(
        'DateProduced',
        storage=atapi.AnnotationStorage(),
        widget=atapi.CalendarWidget(
            label=_(u"Date of release"),
            show_hm = False,
        ),
        languageIndependent=True,
		required=True,
        validators=('isValidDate'),
        schemata='default',                
    ),
            
    atapi.TextField(
        'FullDescription',
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Full Description"),
            description=_(u"The description of the video content"),
        ),
        schemata='default',        
    ),

    atapi.StringField(
        'Countries',
        storage=atapi.AnnotationStorage(),
        widget=CountryWidget(
            label=_(u"Country of origin of the video"),
            i18n_domain='atcw',
        ),
        languageIndependent=True,
        schemata='categorization',        
    ),

    atapi.StringField(
        'Genre',
        storage=atapi.AnnotationStorage(),
        widget=atapi.SelectionWidget(
            label=_(u"Video Genre"),
            i18n_domain='plumi',
        ),
        vocabulary=NamedVocabulary("""video_genre"""),
        languageIndependent=True,
        schemata='categorization',                
    ),

    atapi.LinesField(
        'Categories',
        storage=atapi.AnnotationStorage(),
        widget=atapi.MultiSelectionWidget(
            label=_(u"Topics"),
            description=_(u"Hold down CTRL/COMMAND and click to select multiple topics."),
            i18n_domain='plumi',
        ),
        vocabulary=NamedVocabulary("""video_categories"""),
        languageIndependent=True,
        schemata='categorization',                

    ),

    BlobField(
        'video_file',
        storage=atapi.AnnotationStorage(), 
        primary=True,
        required=True,
        accessor='getIterator',
        mutator='setFile',
        widget=atapi.FileWidget(
            label=_(u"Video File"),
            description=_(u"The uploaded video file"),
        ),
        validators=('isNonEmptyFile'),
        schemata='thumbnail',
        languageIndependent=True,

    ),
    
    atapi.ImageField(
        'thumbnailImage',
        storage=atapi.AnnotationStorage(),
        widget=atapi.ImageWidget(
            label=_(u"Video Thumbnail"),
        ),
        max_size = zconf.ATImage.max_image_dimension,
        validators=(('isNonEmptyFile'),('checkImageMaxSize')),
        schemata='thumbnail',
        languageIndependent=True,
        allowable_content_types=('image/gif','image/jpeg','image/png'),
    ),
    
    atapi.StringField(
        'thumbnailImageDescription',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Thumbnail Image description"),
        ),
        schemata='thumbnail',
    ),    


))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

PlumiVideoSchema['title'].storage = atapi.AnnotationStorage()
PlumiVideoSchema['description'].storage = atapi.AnnotationStorage()
PlumiVideoSchema['description'].required = True
PlumiVideoSchema['subject'].widget = atapi.LinesWidget(label=_(u"Tags"), description=_(u"One per line"))

PlumiVideoSchema.moveField('relatedItems', pos='bottom')
PlumiVideoSchema.moveField('location', before='language')

schemata.finalizeATCTSchema(PlumiVideoSchema, moveDiscussion=False)
PlumiVideoSchema.registerLayer('marshall', BlobMarshaller())

class PlumiVideo(base.ATCTContent):
    """Plumi Video content"""
    implements(IPlumiVideo, IMultiPageSchema)
    
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


    def plumiVideoDuration(self):
      """ Get the duration of the uploaded video file """
      strDuration = ''
      try:
        filename = self.video_file.getBlob().committed()
        if filename:
            videoMetaData = extract(filename)
            tdelta = videoMetaData.get('duration')
            seconds = tdelta.seconds
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)            
            if hours > 0:
                strDuration += "%.2d:" % hours                
            strDuration += "%.2d:%.2d" % (minutes,seconds)
      except:
        pass
        
      return strDuration
          

atapi.registerType(PlumiVideo, PROJECTNAME)
