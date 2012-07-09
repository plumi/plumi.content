import os
import tempfile
import shutil
import transaction

from DateTime import DateTime

from zope import schema
from zope.schema import ValidationError
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IContextSourceBinder
from zope.interface import alsoProvides
from zope.component import getUtility
from zope.event import notify

from z3c.form import button
from z3c.form.browser.image import ImageWidget

from five import grok

from plone.directives import form
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.z3cform.interfaces import IWrappedForm

from Products.Archetypes.config import RENAME_AFTER_CREATION_ATTEMPTS
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFDefault.utils import checkEmailAddress
from Products.CMFDefault.exceptions import EmailAddressInvalid
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ISiteRoot
from Products.statusmessages.interfaces import IStatusMessage

from plumi.content import plumiMessageFactory as _
from plumi.content.interfaces import IPlumiVideoFolder



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
            fields=['Title','Description', 'DateProduced','Language', 'FullDescription', 'Thumbnail', 'License']
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
        default= 'en',
        source=get_video_languages,
    )

    form.widget(FullDescription=WysiwygFieldWidget)
    FullDescription = schema.Text(
        title=_(u"Full Description"), 
        required=False,
        description=_(u"The description of the video content"),
    )

    #FIX: validation
    Thumbnail = schema.Bytes(title=u'Add thumbnail',
                         description=u"We will automatically generate an image, but you may prefer to upload your own",
                         required=False)

    #FIX: proper widget
   # form.widget(License=LicenseWidget)
    License = schema.TextLine(
            title=_(u"License"),
            required=False,
        )

    #FIX
    Genre = schema.Choice(
            title=_(u"Genre"),
            required=False,
            source=get_video_genres,
            default='documentary',
        )

    #FIX
    Country = schema.Choice(
            title=_(u"Country"),
            required=False,
            default= 'AU',
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
    #grok.context(IPlumiVideoFolder)
        
    schema = IPlumiVideo
    ignoreContext = True
 
    label = _(u"Publish your video")
    #description = _(u"...")
    
    def uploaded_file(self):
        session_path = tempfile.gettempdir() + '/' + 'plumitmp/' + self.request['SESSION'].id
        try:
            filename = os.listdir(session_path)[0]
            return {'filename' : filename, 
                    'filesize' : os.stat(session_path + '/' + filename).st_size,
                    'path' : session_path + '/' + filename}
        except:
            return None

    
    def _findUniqueId(self, id):
        """Find a unique id in the current folder, based on the given id, by
        appending -n, where n is a number between 1 and the constant
        RENAME_AFTER_CREATION_ATTEMPTS. If no id can be
        found, return None.
        """
        ids = self.context.objectIds()
        
        if id not in ids:
            return id

        idx = 1
        while idx <= RENAME_AFTER_CREATION_ATTEMPTS:
            new_id = "%s-%d" % (id, idx)
            if not new_id in ids:
                return new_id
            idx += 1

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
        
        # Calculate unique id from title
        uid = str(DateTime().millis())

        # Create the object
        self.context.invokeFactory('PlumiVideo', id=uid, Title=data['Title'],
                                   description=data['Description'],
                                   DateProduced=data['DateProduced'],
                                   VideoLanguage=data['Language'],
                                   FullDescription=data['FullDescription'],
                                   #Genre=data['Genre'],
                                   #Countries=data['Country'],
                                   #location=data['Location'],
                                   #subject=data['Tags'],
                                   #Director=data['Director'],
                                   #Producer=data['Producer'],
                                   #Email=data['Email'],
                                   #ProductionCompanyName=data['ProductionCompany'],
                                   #WebsiteURL=data['Website'],
                                   )
        
        # get the newly created object
        obj = self.context[uid]
        
        # set the video file field and remove temp uploaded file
        path = self.uploaded_file()['path']
        f = open(path)
        obj.setFile(f)
        f.close()
        shutil.rmtree('/'.join(path.split('/')[:-1]), ignore_errors=True)
        
        # Rename with friendly id
        normalizer = getUtility(IIDNormalizer)
        new_id = self._findUniqueId(normalizer.normalize(data['Title']))
        transaction.savepoint(1)
        obj.setId(new_id)
        
        # Reindex and send init event
        obj.reindexObject()
        notify(ObjectInitializedEvent(obj))
        
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
