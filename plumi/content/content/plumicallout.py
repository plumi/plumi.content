"""Definition of the PlumiCallOut content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

#third party products
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary

from plumi.content import contentMessageFactory as _
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
    ),


    atapi.ImageField(
        'calloutImage',
        storage=atapi.AnnotationStorage(),
        widget=atapi.ImageWidget(
            label=_(u"Image"),
            description=_(u"Will be shown in the call out listings, and the call out item itself. Image will be scaled to a sensible size."),
        ),
        required=True,
        validators=('isNonEmptyFile'),
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
        widget=atapi.SelectionWidget(
            label=_(u"Category"),
            description=_(u"Categories. Hold down CTRL/COMMAND and click to multiple select topics."),
        ),
        required=True,
	vocabulary=NamedVocabulary("""submission_categories"""),
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

    calloutImageCaption = atapi.ATFieldProperty('calloutImageCaption')

    calloutImage = atapi.ATFieldProperty('calloutImage')

    bodyText = atapi.ATFieldProperty('bodyText')

    submissionCategories = atapi.ATFieldProperty('submissionCategories')

    closingDate = atapi.ATFieldProperty('closingDate')


atapi.registerType(PlumiCallOut, PROJECTNAME)
