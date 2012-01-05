from Products.Five.browser import BrowserView
from zope.component import getUtility
from collective.transcode.star.interfaces import ITranscodeTool


class reTranscode(BrowserView):

    def __init__(self, context, request):
        super(reTranscode, self).__init__(context, request)

    def __call__(self):
        tt = getUtility(ITranscodeTool)
        res = tt.add(self.context, force=True)
        self.context.reindexObject()
        return res
