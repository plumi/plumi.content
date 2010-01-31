from zope.annotation.interfaces import IAnnotations
from Products.CMFCore.interfaces import IPropertiesTool
from zope.component import getUtility

import transaction
from ZODB.PersistentMapping import PersistentMapping
import xmlrpclib
import urllib
from urlparse import urlparse


def setup_transcoding(obj):
    annotations = IAnnotations(obj, None)
    if not annotations.has_key('plumi.transcode.profiles'):
        annotations['plumi.transcode.profiles'] = PersistentMapping()

    pprop = getUtility(IPropertiesTool)
    config = getattr(pprop, 'plumi_properties', None)
    #TODO Check if we have transcoding support enabled
    address = getattr(config, 'transcodedaemon_address', None)
    if address:
        try:
            transcodeServer=xmlrpclib.ServerProxy(address)
            transcodeProfiles = transcodeServer.getAvailableProfiles()
        except Exception, e:
            print 'ERROR: Could not connect to transcode daemon %s: %s' % (address, e)
            return
        #Submit XML-RPC call to transcoder
        transcodeOptions = dict()
        
        #TODO - get better way of discovering the path to the video file
        path = obj.absolute_url_path()
        if config.plonesite_address:
            plonesite = urlparse(config.plonesite_address)
        else:
            plonesite = urlparse(obj.absolute_url())
        url_format = "%s://%s:%s@%s%s/@@streaming_RPC"

        cb_url = url_format % ( plonesite[0], #protocol
                                config.plonesite_login,
                                config.plonesite_password,
                                plonesite[1], #netloc
                                urllib.quote(path)) #path (for this video)
        transcodeInput=dict(path = ( plonesite[0] + "://" + \
                                     plonesite[1] + path + \
                                     '/download/video_file/' + \
                                     obj.video_file.getFilename()), 
                            type=obj.video_file.getContentType())

        trans = transaction.get()
        for transcodeProfile in transcodeProfiles:
            print "plumi running profile %s" % transcodeProfile
            annotations['plumi.transcode.profiles'][transcodeProfile] = \
                                                        {'status': 1,
                                                         'message': "IN PROGRESS"}

            trans.addAfterCommitHook(transcoding_hook, 
                                    (transcodeServer, transcodeInput, 
                                    transcodeProfile, transcodeOptions, cb_url))

        print "plumi: ConvertDaemon call pending"

def transcoding_hook(status, server, input, profile, options, cb_url):
    """
    """
    if not status:
        return
    try:
        jobId = server.convert(input, profile, options, cb_url)
        print "plumi: ConvertDaemon call "+jobId
    #except xmlrpclib.Error, e:
    except Exception, e:
        print "plumi: ConvertDaemon call FAILED", e
        server=xmlrpclib.ServerProxy(cb_url)
        server.conv_done_xmlrpc(e)
    #print "INPUT ", input_path
    #print "OUTPUT", output_path
    #return jobId
