from zope.interface import implements

from Products.Five  import BrowserView
from zope.annotation.interfaces import IAnnotations

from plumi.content.interfaces.plumivideo import ICallBackView

class CallBackView(BrowserView):
    """
    """
    implements(ICallBackView)

    def conv_done_xmlrpc(self, status, message, profile, URL):
        """
        """
        print "callback: %d %s %s %s" % (status, message, profile, URL)
        annotations = IAnnotations(self.context, None)
        if annotations is None:
            return
#        if not annotations.has_key('plumi.flowplayer.transcode.profiles'):
#            annotations['plumi.transcode.profiles'] = {}
        annotations['plumi.transcode.profiles'][profile] = {'URL':URL, 'status':status, 'message':message}
        #annotations._p_changed = True
        print 'set transcoding: ' + annotations['plumi.transcode.profiles'][profile]['URL']

        #IStreamable(self.context)._storeStreaming(status)

