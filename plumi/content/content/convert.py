from zope.interface import implements
from zope.component import getUtility
from Products.Five  import BrowserView
from zope.annotation.interfaces import IAnnotations
from Products.CMFCore.interfaces import IPropertiesTool
from plumi.content.interfaces.plumivideo import ICallBackView
from urllib import urlopen
import logging
import sys

class CallBackView(BrowserView):
    """
    """
    implements(ICallBackView)

    def conv_done_xmlrpc(self, status, message, profile, path):
        """
        """
        logger = logging.getLogger('plumi.content.callback')
        logger.info("callback: %d %s %s %s" % (status, message, profile, path))
        annotations = IAnnotations(self.context, None)
        if annotations is None:
            return

        annotations['plumi.transcode.profiles'][profile] = {'path':path, 'status':status, 'message':message}
        
        if profile == 'jpeg':        
            imgfield = self.context.getField('thumbnailImage') # check if there is already a thumbnail image
	    logger.info('jpeg callback %s' % imgfield)
            if not imgfield or imgfield.getSize(self.context) == (0, 0): # if not use the image returned by the transcoder
                try:    
		    logger.info('setting thumbnail to %s' % path)
                    pprop = getUtility(IPropertiesTool)
                    plprop = getattr(pprop, 'plumi_properties', None)
                    videoserver = getattr(plprop,'videoserver_address',None)
                    if videoserver: 
                        url = '%s/%s' % (videoserver, path)
                        logger.info("getting thumbnail from %s" % url)
                        f = urlopen(url)
                    else:
                        logger.error("cannot find videoserver: %s %s %s" %(pprop,plrop,videoserver))
                        f = open(path,'r')
                    self.context.setThumbnailImage(f.read())
                    #self.reindexObject()
                    f.close()
                except:
                    logger.error("cannot set thumbnail %s to %s. Error %s" % (path, self.context,sys.exc_info()[0]))
                
        logger.info('set transcoding: ' + annotations['plumi.transcode.profiles'][profile]['path'])

        #IStreamable(self.context)._storeStreaming(status)

