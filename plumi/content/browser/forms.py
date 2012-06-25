
from zope import schema
from zope.schema import ValidationError
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IContextSourceBinder
from z3c.form import button

from five import grok
from plone.directives import form
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

from Products.CMFDefault.utils import checkEmailAddress
from Products.CMFDefault.exceptions import EmailAddressInvalid

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ISiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from zope.interface import alsoProvides
from plone.z3cform.interfaces import IWrappedForm
from plumi.content import plumiMessageFactory as _


class InvalidEmailAddress(ValidationError):
    "Invalid email address"

def validateaddress(value):
    try:
        checkEmailAddress(value)
    except EmailAddressInvalid:
        raise InvalidEmailAddress(value)
    return True


@grok.provider(IContextSourceBinder)
def get_video_languages(context):
    """Fake the genres/categories process to return the video language infos"""
    pv = getToolByName(context, 'portal_vocabularies')
    voc = pv.getVocabularyByName('video_languages')
    languagesDict = []
    voc_terms = voc.getDisplayList(context).items()

    for term in voc_terms:
        languagesDict.append( (term[0], term[1]) )
    return SimpleVocabulary.fromItems(languagesDict)


@grok.provider(IContextSourceBinder)
def get_topics(context):
    """Return the topics"""
    pv = getToolByName(context, 'portal_vocabularies')
    voc = pv.getVocabularyByName('video_categories')
    categoriesDict = []
    voc_terms = voc.getDisplayList(context).items()

    for term in voc_terms:
        categoriesDict.append( (term[0], term[1]) )
    return SimpleVocabulary.fromItems(categoriesDict)


@grok.provider(IContextSourceBinder)
def get_genres(context):
    """Return the genres"""
    pv = getToolByName(context, 'portal_vocabularies')
    voc = pv.getVocabularyByName('video_genre')
    genreDict = []
    voc_terms = voc.getDisplayList(context).items()

    for term in voc_terms:
        genreDict.append( (term[0], term[1]) )
    return SimpleVocabulary.fromItems(genreDict)


@grok.provider(IContextSourceBinder)
def get_countries(context):
    """Return the countries"""
    pv = getToolByName(context, 'portal_vocabularies')
    voc = pv.getVocabularyByName('video_languages')
    countriesDict = []
    voc_terms = voc.getDisplayList(context).items()

    for term in voc_terms:
        countriesDict.append( (term[0], term[1]) )
    return SimpleVocabulary.fromItems(countriesDict)


class IPlumiVideo(form.Schema):
    
    form.fieldset('default',
            label=u"Basic info",
            fields=['Title','Description', 'DateProduced','Language', 'FullDescription']
        )
    
    form.fieldset('categorize',
            label=u"Categorise",
            fields=['Genre', 'Country', 'Location', 'Topics', 'Tags', 'Director',
                'Producer', 'Email', 'Organisation', 'ProductionCompany', 'Website']
        )
    
    Title = schema.TextLine(
            title=_(u"Title"),
            required=True,
        )

    Description = schema.Text(
        title=_(u"Short summary"), 
        required=True,
        description=_(u"Describe your video in 160 characters."),
    )
    
    DateProduced = schema.Date(
        title=_(u"Date Produced"), 
        required=True,
        description=_(u"The date the video content was released."),
    )

    Language = schema.Choice(
        title=_(u"Video Language"),
        required=True,
        source=get_video_languages,
    )

    #FIX: add license, thumbnail

    form.widget(FullDescription=WysiwygFieldWidget)
    FullDescription = schema.Text(
        title=_(u"Full Description"), 
        required=False,
        description=_(u"The description of the video content"),
    )

    #FIX
    Genre = schema.Choice(
            title=_(u"Genre"),
            required=False,
            source=get_genres
        )

    #FIX
    Country = schema.Choice(
            title=_(u"Country"),
            required=False,
            source=get_countries
        )

    Location = schema.TextLine(
            title=_(u"Location"),
            description=_(u"e.g. City or Region."),
            required=False,
        )

    #FIX
    Topics = schema.List(
            title=_(u"Topics"),
            required=False,
            value_type=schema.Choice(source=get_topics),
            default=[],
        )

    #FIX
    Tags = schema.TextLine(
            title=_(u"Tags"),
            required=False,
        )

    Director = schema.TextLine(
            title=_(u"Director"),
            required=False,
        )

    Producer = schema.TextLine(
            title=_(u"Producer"),
            required=False,
        )

    Email = schema.TextLine(
            title=_(u"Email Address"),
            required=False,
            constraint=validateaddress,
        )

    Organisation = schema.TextLine(
            title=_(u"Organisation / Project Name"),
            required=False,
        )

    ProductionCompany = schema.TextLine(
            title=_(u"Production Company"),
            required=False,
        )

    Website = schema.URI(
            title=_(u"Website URL"),
            required=False,
        )


class VideoAddForm(form.SchemaForm):
    grok.name('publish_video')
    grok.require('zope2.View')
    grok.context(ISiteRoot)
        
    schema = IPlumiVideo
    ignoreContext = True
 
    label = _(u"Publish your video")
    #description = _(u"...")
    
    def update(self):
        # disable Plone's editable border
        self.request.set('disable_border', True)
        # alsoProvides(self.form, IWrappedForm)
        # self.form.update()
        # call the base class version - this is very important!
        super(VideoAddForm, self).update()
    
    @button.buttonAndHandler(_(u'SAVE CHANGES'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        
        # Handle order here. For now, just print it to the console. A more
        # realistic action would be to send the order to another system, send
        # an email, or similar
        
        # Redirect back to the front page with a status message

        IStatusMessage(self.request).addStatusMessage(
                _(u"Thank you for publishing the video!"), 
                "info"
            )
        
        contextURL = self.context.absolute_url()
        self.request.response.redirect(contextURL)
        
    @button.buttonAndHandler(_(u"Cancel"))
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """
        contextURL = self.context.absolute_url()
        self.request.response.redirect(contextURL)
