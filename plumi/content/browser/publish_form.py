from Products.Five.browser  import BrowserView
from Products.CMFCore.utils import getToolByName
from zope import i18n

# check if em.taxonomies is installed
try:
    from em.taxonomies.config import TOPLEVEL_TAXONOMY_FOLDER,\
                                        COUNTRIES_FOLDER,\
                                        GENRE_FOLDER,\
                                        CATEGORIES_FOLDER, \
                                        LANGUAGES_FOLDER
    TAXONOMIES = True
except ImportError:
    TAXONOMIES = False


# Internationalization
_ = i18n.MessageFactory("plumi.content")

class PublishForm(BrowserView):
    u"""This browser view is used to populate the video upload form
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.portal_url = getToolByName(self.context, "portal_url")()
        self.vocab_tool = getToolByName(self.context, "portal_vocabularies")

    def get_video_languages(self):
        """Fake the genres/categories process to return the video language infos"""
        voc = self.vocab_tool.getVocabularyByName('video_languages')
        return voc

