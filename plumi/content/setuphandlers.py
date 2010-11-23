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

def plumi30to31(context, logger=None):

    # Migrate callout dates
    catalog = getToolByName(context, 'portal_catalog')
    callouts = catalog(portal_type='PlumiCallOut')
    for c in callouts:
        callout=c.getObject()
        closing = callout.getClosingDate()
        if closing:
            callout.setExpirationDate(closing)
            callout.reindexObject()

    # Migrate video annotations
    catalog = getToolByName(context, 'portal_catalog')
    videos = catalog(portal_type='PlumiVideo')
    tt = getUtility(ITranscodeTool)
    pprop = getUtility(IPropertiesTool)
    config = getattr(pprop, 'plumi_properties', None)

    for video in videos:
        obj = video.getObject()
        UID = obj.UID()
        if not UID:
            continue
        data = StringIO(obj.getField('video_file').get(obj).data)
        md5sum = md5(data.read()).hexdigest()
        annotations = IAnnotations(obj)
        transcode_profiles = annotations.get('plumi.transcode.profiles', {})
        for profile_name in transcode_profiles.keys():
            profile = transcode_profiles[profile_name]
            path = profile.get('path', None)
            if not path:
                continue
            address = config.videoserver_address
            objRec = tt.get(UID, None)
            if not objRec:
                tt[UID] = PersistentDict()

            fieldRec = tt[UID].get('video_file', None)
            if not fieldRec: 
                tt[UID]['video_file']=PersistentDict()
            tt[UID]['video_file'][profile_name] = PersistentDict({'jobId' : None, 'address' : address, 'status' : 'ok', 'start' : datetime.now(), 'md5' : md5sum, 'path': path,})
        if transcode_profiles:
            del annotations['plumi.transcode.profiles']

