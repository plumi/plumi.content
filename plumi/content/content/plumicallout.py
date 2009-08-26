"""Definition of the PlumiCallOut content type
"""

from zope.interface import implements, directlyProvides

try:
    from Products.LinguaPlone import atapi 
except ImportError:
    # No multilingual support
    from Products.Archetypes import atapi

from Products.ATContentTypes.content import base,schemata
from Products.ATContentTypes.configuration import zconf

#third party products
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary

from plumi.content import plumiMessageFactory as _
from plumi.content.interfaces import IPlumiCallOut
from plumi.content.config import PROJECTNAME

PlumiCallOutSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.StringField(
        'websiteURL',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Website Address"),
            description=_(u"Website for more info about the callout"),
        ),
        languageIndependent=True,
    ),

    atapi.StringField(
        'location',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Location"),
            description=_(u"Typically a callout has an associated location in a common format (i.e. City, State)"),
        ),
        languageIndependent=True,
    ),


    atapi.ImageField(
        'calloutImage',
        storage=atapi.AnnotationStorage(),
        widget=atapi.ImageWidget(
            label=_(u"Image"),
            description=_(u"Will be shown in the call out listings, and the call out item itself. Image will be scaled to a sensible size."),
        ),
        required=True,
	    max_size = zconf.ATImage.max_image_dimension,
        validators=(('isNonEmptyFile'),('checkImageMaxSize')),
        languageIndependent=True,
    ),

    atapi.StringField(
        'calloutImageCaption',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Image caption"),
            description=_(u"The text caption describing the image."),
        ),
        required=True,
    ),



    atapi.TextField(
        'bodyText',
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Body Text"),
            description=_(u"The main description for the callout"),
        ),
        required=True,
    ),


    atapi.StringField(
        'submissionCategories',
        storage=atapi.AnnotationStorage(),
        widget=atapi.MultiSelectionWidget(
            label=_(u"Category"),
            description=_(u"Categories. Hold down CTRL/COMMAND and click to multiple select topics."),
            i18n_domain='plumi'
        ),
        required=True,
        vocabulary=NamedVocabulary("""submission_categories"""),
        languageIndependent=True,
    ),


    atapi.DateTimeField(
        'closingDate',
        storage=atapi.AnnotationStorage(),
        widget=atapi.CalendarWidget(
            label=_(u"Closing Date"),
            description=_(u"Provide a date for when this callout will be closed."),
        ),
        required=True,
        validators=('isValidDate'),
        languageIndependent=True,
    ),


))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

PlumiCallOutSchema['title'].storage = atapi.AnnotationStorage()
PlumiCallOutSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(PlumiCallOutSchema, moveDiscussion=False)

class PlumiCallOut(base.ATCTContent):
    """Call out for help with production of video content"""
    implements(IPlumiCallOut)

    meta_type = "PlumiCallOut"
    schema = PlumiCallOutSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    websiteURL = atapi.ATFieldProperty('websiteURL')

    location = atapi.ATFieldProperty('location')

    calloutImageCaption = atapi.ATFieldProperty('calloutImageCaption')

    calloutImage = atapi.ATFieldProperty('calloutImage')

    bodyText = atapi.ATFieldProperty('bodyText')

    submissionCategories = atapi.ATFieldProperty('submissionCategories')

    closingDate = atapi.ATFieldProperty('closingDate')


atapi.registerType(PlumiCallOut, PROJECTNAME)
