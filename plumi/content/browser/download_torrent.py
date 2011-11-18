# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse, NotFound

from Acquisition import aq_base
from Products.Five.browser import BrowserView

from zope.component import getUtility
from plone.registry.interfaces import IRegistry
import os.path
from httplib import HTTPResponse
import urllib


class DownloadTorrent(BrowserView):
    """Download a torrent file, via ../context/@@download_torrent
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(DownloadTorrent, self).__init__(context, request)
        self.fieldname = None

    def publishTraverse(self, request, name):
        if self.fieldname is None:  # ../@@download/fieldname
            self.fieldname = name
        else:
            raise NotFound(self, name, request)
        return self

    def __call__(self):
        registry = getUtility(IRegistry)
        torrent_dir = registry['collective.seeder.interfaces.ISeederSettings.safe_torrent_dir']
        torrentName = self.context.UID() + '_' + self.context.video_file.getFilename() + '.torrent'
        torrentPath = os.path.join(torrent_dir, torrentName)

        if os.path.exists(torrentPath):
            fo = open(torrentPath, "rb")
            str = fo.read()
            fo.close()
            self.request.response.setHeader("Content-Type",
                                            "application/x-torrent")
            self.request.response.setHeader("Content-Length",
                                            os.path.getsize(torrentPath))
            self.request.response.setHeader("Content-Disposition",
                                    "attachment; filename=\"%s\"" % torrentName)
            return str
        else:
            raise NotFound(self, self.context, self.request)
