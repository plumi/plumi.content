import socket
import urllib
import urllib2
from urllib2 import HTTPError

import logging
logger = logging.getLogger("plumi.content")


OEMBED_PROVIDERS = {
    'youtube': {
        'endpoint': 'http://www.youtube.com/oembed',
        'extraParams': 'format=json',
    },
    'vimeo': {
        'endpoint': 'http://vimeo.com/api/oembed.json'
    }
}


class OembedProxyView(object):
    
    
    def __init__(self, context, request):
      self.context = context
      self.request = request
    
     
    def __call__(self):
        providerName = self.request.get('provider')
        url = self.request.get('url')
        # TODO: more comprehensive set of oembed parameters - see
        # (http://oembed.com/) ?
        maxwidth = self.request.get('maxwidth') or '525'
        #logger.info('proxy call in progress')
        if not providerName:
            raise Exception("the 'provider' parameter is required")
        if not url:
            raise Exception("the 'url' parameter is required")
        oembedProvider = OEMBED_PROVIDERS[providerName];
        #logger.info('oembed provider:' + repr(oembedProvider))
        queryUrl = oembedProvider['endpoint'] + '?' + urllib.urlencode({
            'url' : url,
            'maxwidth' : maxwidth
        });
        #logger.info('query URL:' + repr(queryUrl))
        extraParams = oembedProvider.get('extraParams')
        if extraParams != None:
            queryUrl = queryUrl + '&' + extraParams;
        
        #logger.info('making oembed request:' + repr(queryUrl))
        req = urllib2.Request(queryUrl)
        try:
            response = urllib2.urlopen(req)
            #logger.info('oembed request was successful')
            return response.read()
        except HTTPError, e:
            logger.error("oembed request failed:" + e.read())
            raise e
