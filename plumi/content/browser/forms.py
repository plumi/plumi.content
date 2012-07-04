import os
import tempfile
import shutil

from zope import schema
from zope.schema import ValidationError
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
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

from zope.component import getUtility
from plone.uuid.interfaces import IUUIDGenerator

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
    return get_vocabulary_items(context, 'video_languages')


@grok.provider(IContextSourceBinder)
def get_video_countries(context):
    return get_vocabulary_items(context, 'video_countries')

@grok.provider(IContextSourceBinder)
def get_video_genres(context):
    return get_vocabulary_items(context, 'video_genre')


@grok.provider(IContextSourceBinder)
def get_video_categories(context):
    return get_vocabulary_items(context, 'video_categories')


def get_vocabulary_items(context, vocabulary):
    """Return the vocabulary item"""
    pv = getToolByName(context, 'portal_vocabularies')
    voc = pv.getVocabularyByName(vocabulary)
    countriesDict = []
    voc_terms = voc.getDisplayList(context).items()

    countriesDict = [ SimpleTerm(value=term[0], token=term[0], title=term[1]) for term in voc_terms]

    return SimpleVocabulary(countriesDict)


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
        default=('en', 'English'),
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
            source=get_video_genres
        )

    #FIX
    Country = schema.Choice(
            title=_(u"Country"),
            required=False,
            default="Australia",
            source=get_video_countries
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
            value_type=schema.Choice(source=get_video_categories),
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
    grok.require('cmf.AddPortalContent')
    grok.context(ISiteRoot)
        
    schema = IPlumiVideo
    ignoreContext = True
 
    label = _(u"Publish your video")
    #description = _(u"...")
    
    def uploaded_file(self):
        session_path = tempfile.gettempdir() + '/' + 'plumitmp/' + self.request['SESSION'].id
        try:
            filename = os.listdir(session_path)[0]
            return {'filename' : filename, 
                    'filesize' : os.stat(session_path + '/' + filename).st_size}
        except:
            return None
    
    def update(self):
        # disable Plone's editable border
        self.request.set('disable_border', True)
        # call the base class version - this is very important!
        super(VideoAddForm, self).update()
    
    @button.buttonAndHandler(_(u'Save changes'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        
        if not self.uploaded_file():
            self.status = _(u"No file was uploaded")
            return
        
        # TODO: Handle video creation here
        
        
        # Redirect back to the front page with a status message
        IStatusMessage(self.request).addStatusMessage(
                _(u"Thank you for your contribution!"), 
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
