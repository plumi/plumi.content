# -*- coding: utf-8 -*-
import urllib2
import simplejson
import os.path
from subprocess import Popen, PIPE
from random import sample

# Five & zope3 thingies
from zope import i18n
from zope.interface import implements
from Products.Five.browser  import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from zope.component import queryMultiAdapter

# CMF
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFCore.utils import getToolByName

from plumi.content.browser.interfaces import IVideoView, ITopicsProvider, IAuthorPage, IPlumiVideoBrain
from collective.mediaelementjs.interfaces import IMediaInfo
from collective.transcode.star.interfaces import ITranscodeTool

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


class VideoView(BrowserView):
    u"""This browser view is used as utility for the atvideo view
    """
    implements(IVideoView, ITopicsProvider)

    def __init__(self, context, request):
        super(VideoView, self).__init__(context, request)
        self.portal_url = getToolByName(self.context, "portal_url")()
        self.vocab_tool = getToolByName(self.context, "portal_vocabularies")
        pprop = getUtility(IPropertiesTool)

    @property
    def video_info(self):
        annotations = IAnnotations(self.context, None)
        return annotations.get('plumi.video_info')

    @property
    def categories(self):
        categories = self.context.getCategories()
        if categories:
            return self.get_categories_dict(categories)
        return tuple()

    @property
    def genres(self):
        """Actually, the genre is unique. We masquarade that.
        We might want the genre to be multivalued.
        """
        genres = self.context.getGenre()
        if genres and genres not in ['none', 'aaa_none']:
            return self.get_genres_info((genres,))
        return tuple()

    @property
    def subjects(self):
        subjects = self.context.Subject()
        if subjects:
            return self.get_subjects_info(subjects)
        return tuple()

    @property
    def country(self):
        country_id = self.context.getCountries()
        if country_id in ['OO', 'none', '']:
            return None
        if country_id:
            return self.get_country_info(country_id)
        return None

    @property
    def video_language(self):
        video_language_id = self.context.getVideoLanguage()
        if video_language_id:
            return self.get_video_language_info(video_language_id)
        return None

    @property
    def language(self):
        lang_id = self.context.Language()
        if lang_id:
            return self.get_country_info(lang_id)
        return None

    @property
    def review_state(self):
        wtool = getToolByName(self.context, "portal_workflow")
        return wtool.getInfoFor(self.context, 'review_state', None)

    @property
    def transcoding_rights(self):
        # TODO: this is ugly! we shouldn't check for role names but for permissions
        mtool = getToolByName(self.context, "portal_membership")
        member = mtool.getAuthenticatedMember()
        mb_id = member.getUserName()
        member_roles = member.getRoles()

        is_manager = 'Manager' in member_roles
        is_reviewer = 'Reviewer' in member_roles
        is_owner = mb_id in self.context.users_with_local_role('Owner')
        """Return is_manager or is_owner. XXX make this an configurable option,
        ie settable thru a configelet whether or not owner can see this
        template, but for now just make it is_manager or is_reviewer.
        """
        return is_manager or is_reviewer

    @property
    def bt_availability(self):
        """XXX fix bittorrent functionality
        media_tool = getToolByName(self.context, "portal_atmediafiletool")
        enabled_bt = media_tool.getEnable_bittorrent()
        enable_ext_bt = media_tool.getEnable_remote_bittorrent()
        bt_url = self.context.getTorrentURL()
        """
        bt_url = ''

        available = False
        return dict(available=available, url=bt_url)

    def playable(self):
        """ Is the source video in a web friendly format? """
        return len([ True for ext in ['.webm','.mp4','.m4v']
                    if self.context.video_file.filename.endswith(ext)])
    
    @property    
    def transcoding(self):
        ret = {}
        try:
            tt = getUtility(ITranscodeTool)
            entry = tt[self.context.UID()]['video_file']
            for k in entry.keys():
                ret[k] = [entry[k]['status'],
                          entry[k]['status'] == 'ok' and entry[k]['address'] + '/' + entry[k]['path'] or \
                          entry[k]['status'] == 'pending' and \
                          tt.getProgress(entry[k]['jobId']) or '0']
            return ret
        except Exception, e:
            return False

    def get_categories_dict(self, cats):
        """Uses the portal vocabularies to retrieve the video categories"""
        voc = self.vocab_tool.getVocabularyByName('video_categories')

        if not TAXONOMIES:
            url = "%s/search?getCategories=" % (self.portal_url)
        else:
            url = "%s/%s/%s/" % (self.portal_url,
                             TOPLEVEL_TAXONOMY_FOLDER, CATEGORIES_FOLDER)
        return (dict(id=cat_id,
                     url=url + cat_id,
                     title=voc.get(cat_id, None) and voc[cat_id].Title()) for cat_id in cats)

    def get_genres_info(self, genres):
        """Uses the portal vocabularies to retrieve the video genres"""
        voc = self.vocab_tool.getVocabularyByName('video_genre')

        if not TAXONOMIES:
            url = "%s/search?getGenre=" % self.portal_url
        else:
            url = "%s/%s/%s/" % (self.portal_url,
                                 TOPLEVEL_TAXONOMY_FOLDER, GENRE_FOLDER)
        return (dict(id=genre_id,
                     url=url + genre_id,
                     title=voc[genre_id].Title()) for genre_id in genres)

    def get_subjects_info(self, subjects):
        """Fake the genres/categories process to return keywords infos"""
        url = "%s/search?Subject=" % (self.portal_url)
        return (dict(id=kw, url=url + kw, title=kw) for kw in subjects)

    def get_country_info(self, country_id):
        """Fake the genres/categories process to return the country infos"""
        voc = self.vocab_tool.getVocabularyByName('video_countries')
        country = voc[country_id]

        if not TAXONOMIES:
            url = "%s/search?getCountries=" % self.portal_url
        else:
            url = "%s/%s/%s/" % (self.portal_url,
                                 TOPLEVEL_TAXONOMY_FOLDER, COUNTRIES_FOLDER)
        return dict(id=country_id, url=url + country_id, title=country.Title())

    def get_video_language_info(self, video_language_id):
        """Fake the genres/categories process to return the video language infos"""
        voc = self.vocab_tool.getVocabularyByName('video_languages')
        video_language = voc[video_language_id]
        if not TAXONOMIES:
            url = "%s/search?getCountries=" % self.portal_url
        else:
            url = "%s/%s/%s/" % (self.portal_url, TOPLEVEL_TAXONOMY_FOLDER, LANGUAGES_FOLDER)
        return dict(id=video_language_id, url=url + video_language_id, title=video_language.Title())

    def authors_latest(self):
        folder_path = '/'.join(self.context.aq_inner.aq_parent.getPhysicalPath())
        catalog = getToolByName(self.context, "portal_catalog")
        query = dict(portal_type='PlumiVideo',
                     path={'query': folder_path, 'depth': 1},
                     sort_on='effective',
                     sort_order='reverse',
                     review_state=['published', 'featured'])
        try:
            brains = sample(catalog(**query), 5)
        except:
            res = []
            for brain in catalog(**query):
                if not brain.UID in self.context.UID():
                    """ this is not nice, tho limited to less than five
                    getObjects it should be improved
                    """
                    item = brain.getObject()
                    if item.getThumbnailImage() is not None and\
                    item.getThumbnailImage() is not '':
                        res.append(brain)
            brains = res
        return [queryMultiAdapter((brain, self), IPlumiVideoBrain)
                for brain in brains]

    @property
    def post_date(self):
        date = self.context.effective()
        if not date or date.year() == 1000:
            date = self.context.created()
        return self.context.toLocalizedTime(date)

    def hasThumbnailImage(self):
        if getattr(self.context, 'thumbnailImage', None) is None:
                return False
        imgfield = self.context.getField('thumbnailImage')
        #XXX test if the field is ok
        if imgfield is None or imgfield is '' or\
        imgfield.getSize(self.context) == (0, 0):
            return False
        return True

    @property
    def has_torrent(self):
        try:
            registry = getUtility(IRegistry)
            seeder = [i for i in getToolByName(self.context,
                        "portal_quickinstaller").listInstalledProducts()
                      if i['id']=='collective.seeder']
            if not seeder:
                return False
            torrent_dir = registry['collective.seeder.interfaces.ISeederSettings.safe_torrent_dir']
            torrentPath = os.path.join(torrent_dir, self.context.UID() + '_' +\
                            self.context.video_file.getFilename()) + '.torrent'
            if os.path.exists(torrentPath):
                return True
            else:
                return False
        except:
            return False


class SeedersView(BrowserView):
    u"""This browser view is used to return the torrent seeders for the video
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'application/json')
        result = self.getSeeders()
        return simplejson.dumps(result)

    def getSeeders(self):
        """ Return number of seeders from torrent client"""
        try:
            registry = getUtility(IRegistry)
            torrent_dir = registry['collective.seeder.interfaces.ISeederSettings.safe_torrent_dir']
            torrentPath = os.path.join(torrent_dir, self.context.UID() + '_' +\
                            self.context.video_file.getFilename()) + '.torrent'
            if os.path.exists(torrentPath):
                torrent_info_args = ['deluge-console', 'info']
                output = Popen(torrent_info_args, stdout=PIPE).communicate()[0]
                start = output.find(self.context.UID())
                output2 = output[start:]
                end = output2.find(') Peers')
                output3 = output2[:end]
                start2 = output3.find('Seeds: 0 (')
                if output3[(start2+10):] == '':
                    seeders = 0
                else:
                    seeders = output3[(start2+10):]
                    return seeders
            else:
                return 0
        except:
            return 0


class flowplayerConfig(BrowserView):

    def transcoding(self, profile):
        if profile in self.transcode_profiles:
            if self.transcode_profiles[profile]['status'] == 0:
                return self.transcode_profiles[profile]['URL']
        return ''

    def __call__(self, request=None, response=None):

        self.request.response.setHeader("Content-type", "text/javascript")

        self.annotations = IAnnotations(self.context)
        self.transcode_profiles = self.annotations.get('plumi.transcode.profiles')
        if not self.transcode_profiles:
            self.transcode_profiles = {}
        return """
{
    'embedded': 'true',
    // common clip properties
    'clip': {
        'url': '%s',
    },
    'plugins': {
        // use youtube controlbar
        'controls': {
            'url': '%s/%%2B%%2Bresource%%2B%%2Bplumi.content.flowplayer/flowplayer.controls-3.2.1.swf'
            'height': 30,
            'backgroundColor': '#115233'
        }
    }
}
        """ % (self.transcoding('mp4'), self.portal_url, )
