from hashlib import md5
from datetime import datetime
from StringIO import StringIO
import logging
from Products.CMFCore.utils import getToolByName
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from Products.CMFCore.interfaces import IPropertiesTool
from collective.transcode.star.interfaces import ITranscodeTool



def migrate_annotations(context, logger=None):
    catalog = getToolByName(context, 'portal_catalog')
    videos = catalog(portal_type='PlumiVideo')
    tt = getUtility(ITranscodeTool)
    pprop = getUtility(IPropertiesTool)
    config = getattr(pprop, 'plumi_properties', None)

    for video in videos[:5]:
        obj = video.getObject()
        data = StringIO(obj.getField('video_file').get(obj).data)
        md5sum = md5(data.read()).hexdigest()
        annotations = IAnnotations(obj)
        transcode_profiles = annotations.get('plumi.transcode.profiles')
        for transcode_profile in transcode_profiles.keys():
            path = transcode_profile.get('path', None)
            if not path:
                continue
            address = config.videoserver_address
            entry = tt[obj.UID()]['video_file'][transcode_profile]
            objRec = tt.get(UID, None)
            if not objRec:
                tt[UID] = PersistentDict()
            fieldRec = tt[UID].get('video_file', None)
            if not fieldRec: 
                tt[UID]['video_file']=PersistentDict()
            tt[UID]['video_file'][transcode_profile] = PersistentDict({'jobId' : None, 'address' : address, 'status' : 'ok', 'start' : datetime.now(), 'md5' : md5sum})


def import_various(context):
    if context.readDataFile('plumi.content-default.txt') is None:
        return
    logger = context.getLogger('your.package')
    site = context.getSite()
    add_catalog_indexes(site, logger)

