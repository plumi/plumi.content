from Products.Five.browser import BrowserView
from collective.transcode.star.interfaces import ITranscodeTool
from zope.component import getUtility

class reTranscode(BrowserView):

    def __init__(self, context, request):
        super(reTranscode, self).__init__(context, request)

    def __call__(self):
        tt = getUtility(ITranscodeTool)
        return tt.add(self.context, force=True)
