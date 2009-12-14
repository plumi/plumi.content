from zope.interface import implements

from Products.Five  import BrowserView
from zope.annotation.interfaces import IAnnotations

from plumi.content.interfaces.plumivideo import ICallBackView

class CallBackView(BrowserView):
    """
    """
    implements(ICallBackView)

    def conv_done_xmlrpc(self, status, message, profile, URI):
        """
        """
        print "callback: %d %s %s %s" % (status, message, profile, URI)
        annotations = IAnnotations(self.context, None)
        if annotations is None:
            return
#        if not annotations.has_key('plumi.flowplayer.transcode.profiles'):
#            annotations['plumi.transcode.profiles'] = {}
        annotations['plumi.transcode.profiles'][profile] = {'URI':URI, 'status':status, 'message':message}
        annotations._p_changed = True
        print 'set transcoding: ' + annotations['plumi.transcode.profiles'][profile]['URI']

        #IStreamable(self.context)._storeStreaming(status)

