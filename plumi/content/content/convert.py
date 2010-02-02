from zope.interface import implements

from Products.Five  import BrowserView
from zope.annotation.interfaces import IAnnotations

from plumi.content.interfaces.plumivideo import ICallBackView
from urllib import urlretrieve

class CallBackView(BrowserView):
    """
    """
    implements(ICallBackView)

    def conv_done_xmlrpc(self, status, message, profile, path):
        """
        """
        print "callback: %d %s %s %s" % (status, message, profile, path)
        annotations = IAnnotations(self.context, None)
        if annotations is None:
            return
#        if not annotations.has_key('plumi.flowplayer.transcode.profiles'):
#            annotations['plumi.transcode.profiles'] = {}
        annotations['plumi.transcode.profiles'][profile] = {'path':path, 'status':status, 'message':message}
        #annotations._p_changed = True
        if profile == 'jpeg':
            try:
                [ thumbPath, re ] = urlretrieve(path)            
                f = open(path,'r')
                self.context.setThumbnailImage(f)
                f.close()
            except:
                print "cannot set thumbnail %s to %s" % (path, self.context)
                
        print 'set transcoding: ' + annotations['plumi.transcode.profiles'][profile]['path']

        #IStreamable(self.context)._storeStreaming(status)

