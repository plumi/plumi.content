import os, re, tempfile, shutil, datetime
import transaction
from DateTime import DateTime

from PIL import Image
import StringIO

from zope import schema
from zope.schema import ValidationError
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IContextSourceBinder
from zope.interface import alsoProvides
from zope.component import getUtility, adapter
from zope.event import notify

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from z3c.form import button
from z3c.form import widget

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
from Products.CMFCore.interfaces import ISiteRoot, IFolderish
from Products.statusmessages.interfaces import IStatusMessage
from plone.registry.interfaces import IRegistry

from collective.contentlicensing.utilities.interfaces import IContentLicensingUtility
from collective.contentlicensing.DublinCoreExtensions.interfaces import ILicense

from plumi.content import plumiMessageFactory as _
from plumi.content.interfaces import IPlumiVideoFolder

from urlparse import urlparse

class InvalidEmailAddress(ValidationError):
    "Invalid email address"


class InvalidImage(ValidationError):
    "Please upload a valid image file"

class InvalidURI(ValidationError):
    "Invalid Website URI"

class InvalidDate(ValidationError):
    "Year must be between 1900 and the current year"

def validate_address(value):
    try:
        checkEmailAddress(value)
    except EmailAddressInvalid:
        raise InvalidEmailAddress(value)
    return True

def validate_image(value):
    try:
        im = Image.open(StringIO.StringIO(value))
    except:
        raise InvalidImage
    return True

def validate_date(value):
    try:
        if not 1900<=int(value)<=datetime.datetime.now().year:
            raise InvalidDate
    except:
        raise InvalidDate
    return True

def validate_URI(value):
    if not (value.startswith('http://') or value.startswith('https://')):
        value = 'http://' + value 
    try:
        is_valid_url(value)
    except:
        raise InvalidURI(value)
    if not is_valid_url(value):
        raise InvalidURI(value)
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
    countriesDict = [SimpleTerm(value=term[0], token=term[0], title=term[1])
                     for term in voc_terms]
    return SimpleVocabulary(countriesDict)


class IPlumiVideo(form.Schema):
    """ Publish video form schema """

    form.fieldset('categorize',
                  label=u"Categorise",
                  fields=['Genre', 'Country', 'Topics', 'Tags', 'Location',
                          'Director', 'Producer', 'Email', 'Organisation',
                          'ProductionCompany', 'Website']
                  )

    Title = schema.TextLine(title=_(u"Title"),
                            max_length=160,
                            required=True,
                            )

    Description = schema.Text(title=_(u"Short summary"),
                              required=True,
                              max_length=160,
                              description=_(u"Describe your video in 160 characters."),
                              )

    DateProduced = schema.TextLine(title=_(u"Year Produced"),
                               required=True,
                               description=_(u"The year the video content was released."),
                               constraint=validate_date,
                               )

    Language = schema.Choice(title=_(u"Video Language"),
                             required=True,
                             default='en',
                             source=get_video_languages,
                             )

    form.widget(FullDescription=WysiwygFieldWidget)
    FullDescription = schema.Text(title=_(u"Full Description"),
                                  required=False,
                                  )

    #FIX: find a more native validation -eg provided by zope.schema
    Thumbnail = schema.Bytes(title=u'Add thumbnail',
                             constraint=validate_image,
                             description=u"We will automatically generate an image, but you may prefer to upload your own",
                             required=False,
                             )

    License = schema.TextLine(title=_(u"License"),
                              required=False,
                              )

    Genre = schema.Choice(title=_(u"Genre"),
                          required=False,
                          source=get_video_genres,
                          default='none',
                          )

    Country = schema.Choice(title=_(u"Country"),
                            required=False,
                            default='XX',
                            source=get_video_countries
                            )

    Location = schema.TextLine(title=_(u"Location"),
                               description=_(u"e.g. City or Region."),
                               required=False,
                               )

    Topics = schema.List(title=_(u"Topics"),
                         required=False,
                         description=_(u"Select topics and click arrows to add or remove"),
                         value_type=schema.Choice(source=get_video_categories),
                         default=[],
                         )

    Tags = schema.TextLine(title=_(u"Tags"),
                           description=_(u"Seperate with comma. Eg tag1, tag2, tag4"),
                           required=False,
                           )

    Director = schema.TextLine(title=_(u"Director"),
                               required=False,
                               )

    Producer = schema.TextLine(title=_(u"Producer"),
                               required=False,
                               )

    Email = schema.TextLine(title=_(u"Email Address"),
                            required=False,
                            constraint=validate_address,
                            )

    Organisation = schema.TextLine(title=_(u"Project Name"),
                                   required=False,
                                   )

    ProductionCompany = schema.TextLine(title=_(u"Production Company"),
                                        required=False,
                                        )

    Website = schema.TextLine(title=_(u"Website URL"),
                         required=False,
                         constraint=validate_URI,
                         )


class VideoAddForm(form.SchemaForm):
    grok.name('publish_video')
    grok.require('cmf.AddPortalContent')
    grok.context(IFolderish)

    schema = IPlumiVideo
    ignoreContext = True

    label = _(u"Publish your video")
    #description = _(u"...")

    def uploaded_file(self):
        pm = getToolByName(self.context,'portal_membership')
        userId = pm.getAuthenticatedMember().id
        session_path = tempfile.gettempdir() + '/' + 'plumitmp/' + userId
        try:
            filename = os.listdir(session_path)[0]
            return {'filename': filename,
                    'filesize': os.stat(session_path + '/' + filename).st_size,
                    'path': session_path + '/' + filename}
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

    @button.buttonAndHandler(_(u'Save changes'), name='apply')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            if len(errors) == 1:
                if errors[0].field.getName() == "Email":
                    self.status = _(u'Invalid E-mail address')
                elif errors[0].field.getName() == "Website":
                    self.status = _(u'Invalid Website URI')
            else:
                self.status = self.formErrorsMessage
            return

        if not self.uploaded_file():
            self.status = _(u"No file was uploaded")
            return

        # Calculate unique id from title
        uid = str(DateTime().millis())

        if data['Tags']:
            subject = data['Tags'].replace(' ', '').split(',')
        else:
            subject = ''
        
        try:
            if data['Website']:
                if not data['Website'].startswith('http://'):
                    data['Website'] = 'http://' + data['Website']
        except:
            pass

        self.create_object(self.context, data, uid, subject)

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
        obj.setTitle(data['Title'])

        # Reindex and send init event
        obj.reindexObject()
        notify(ObjectInitializedEvent(obj))

        # Redirect back to the front page with a status message
        registry = getUtility(IRegistry)
        message = registry['plumi.content.browser.interfaces.IPlumiSettings.AfterVideoText']
        IStatusMessage(self.request).addStatusMessage(message,"info")
        contextURL = obj.absolute_url()
        self.request.response.redirect(contextURL)

    @button.buttonAndHandler(_(u"Cancel"))
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """
        contextURL = self.context.absolute_url()
        self.request.response.redirect(contextURL)

    def updateWidgets(self):
        super(VideoAddForm, self).updateWidgets()
        self.default_fieldset_label = _('Basic info')
        self.widgets["License"].template = ViewPageTemplateFile("forms_templates/ccwidget.pt")

    def create_object(self, context, data, uid, subject):
        context.invokeFactory('PlumiVideo', id=uid,
                                   description=data['Description'],
                                   DateProduced=data['DateProduced'],
                                   VideoLanguage=data['Language'],
                                   FullDescription=data['FullDescription'],
                                   thumbnailImage=data['Thumbnail'],
                                   Genre=data['Genre'],
                                   Countries=data['Country'],
                                   location=data['Location'],
                                   Categories=data['Topics'],
                                   subject=subject,
                                   Director=data['Director'] or '',
                                   Producer=data['Producer'] or '',
                                   ProducerEmail=data['Email'] or '',
                                   ProductionCompanyName=data['ProductionCompany'] or '',
                                   ProjectName=data['Organisation'] or '',
                                   WebsiteURL=data['Website'] or '',
                                   )

def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if not regex.search(url):
        return False
    return True
