from Products.Five.browser import BrowserView
from plumi.content.transcoding import setup_transcoding

class reTranscode(BrowserView):

    def __init__(self, context, request):
        super(reTranscode, self).__init__(context, request)

    def __call__(self):
        return setup_transcoding(self.context)
