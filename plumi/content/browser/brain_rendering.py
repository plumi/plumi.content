# -*- coding: utf-8 -*-
from Acquisition import Explicit
from zope.interface import implements
from zope.component import adapts
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plumi.content.browser.interfaces import IAbstractCatalogBrain
from interfaces import IPlumiVideoBrain, ITopicsProvider
from zope.component import getUtility
from Products.CMFCore.interfaces import IPropertiesTool
from plumi.content.browser.video import VideoView
from collective.transcode.star.interfaces import ITranscodeTool


class PlumiVideoBrain(Explicit):
    u"""Basic Plumi implementation of a video brain renderer.
    """

    implements(IPlumiVideoBrain)
    adapts(IAbstractCatalogBrain, ITopicsProvider)

    template = ViewPageTemplateFile('templates/video_brain.pt')
    __allow_access_to_unprotected_subobjects__ = True

    def __init__(self, context, provider):
        self.context = context
        self.video = context
        self.url = context.getURL()
        self.video_title = context.Title or context.id or 'Untitled'
        self.creator = context.Creator
        try:
            if context.total_comments == 0:
                self.total_comments = "0"
            else:
                self.total_comments = context.total_comments
        except:
            #return None if plone.app.discussion is not installed
            self.total_comments = None
        self.__parent__ = provider
        self.request = getattr(self.context, "REQUEST", None)

    def render_listing(self):
        return self.template.__of__(self.request)(show_title=True,
                                                  feature_video=False)

    def render(self):
        return self.template.__of__(self.request)(show_title=False,
                                                  feature_video=False)

    def render_feature_video(self):
        return self.template.__of__(self.request)(show_title=False,
                                                  feature_video=True)

    @property
    def categories(self):
        if self.video['getCategories'] == 'none' or\
        self.video['getCategories'] == ():
            return tuple()
        return VideoView(self.__parent__.context,
        self.__parent__.request).get_categories_dict(self.video['getCategories'])

    @property
    def country(self):
        if self.video['getCountries'] == '' or\
        self.video['getCountries'] == 'none':
            return None
        return VideoView(self.__parent__.context,
        self.__parent__.request).get_country_info(self.video['getCountries'])

    @property
    def video_language(self):
        if self.video['getVideoLanguage'] == '' or\
        self.video['getVideoLanguage'] == 'none':
            return None
        if not self.video['getVideoLanguage']:
            return None
        return VideoView(self.__parent__.context,
        self.__parent__.request).get_video_language_info(self.video['getVideoLanguage'])

    @property
    def post_date(self):
        date = self.video.effective
        if not date or date.year() == 1000:
            date = self.video.created
        return self.context.toLocalizedTime(date)

    def transcoded(self, uid, profile):
        try:
            tt = getUtility(ITranscodeTool)
            entry = tt[uid]['video_file'][profile]
            return '%s/%s' % (entry['address'], entry['path'])
        except:
            return False
