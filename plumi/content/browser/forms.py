
from zope import schema
from z3c.form import button

from five import grok
from plone.directives import form
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ISiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from zope.interface import alsoProvides
from plone.z3cform.interfaces import IWrappedForm
from plumi.content import plumiMessageFactory as _

class IPlumiVideo(form.Schema):
    
    form.fieldset('default',
            label=u"Basic info",
            fields=['Title','Description', 'DateProduced', 'FullDescription']
        )
    
    form.fieldset('categorize',
            label=u"Categorise",
            fields=['Producer',]
        )
    
    Title = schema.TextLine(
            title=_(u"Title"),
            required=True,
        )

    Description = schema.Text(
        title=_(u"Short summary"), 
        required=True,
    )
    
    DateProduced = schema.Date(
        title=_(u"Date Produced"), 
        required=True,
        description=_(u"The date the video content was released."),
    )

    form.widget(FullDescription=WysiwygFieldWidget)
    FullDescription = schema.Text(
        title=_(u"Full Description"), 
        required=False,
        description=_(u"The description of the video content"),
    )

    Producer = schema.TextLine(
            title=_(u"Producer"),
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
        alsoProvides(self.form, IWrappedForm)
        #self.form.update()
        # call the base class version - this is very important!
        super(VideoAddForm, self).update()
    
    @button.buttonAndHandler(_(u'Order'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        
        # Handle order here. For now, just print it to the console. A more
        # realistic action would be to send the order to another system, send
        # an email, or similar
        
        print u"Order received: %s" % data


        # Redirect back to the front page with a status message

        IStatusMessage(self.request).addStatusMessage(
                _(u"Thank you for your order. We will contact you shortly"), 
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

    def get_video_languages(self):
        """Fake the genres/categories process to return the video language infos"""
        pv = getToolByName(self.context, 'portal_vocabularies')
        voc = pv.getVocabularyByName('video_languages')
        lanugagesDict = []        
        voc_terms = voc.getDisplayList(self).items()

        for term in voc_terms:
            lanugagesDict.append( (term[0], term[1]) )
        return lanugagesDict