from Products.Five.browser  import BrowserView

class PublishForm(BrowserView):
    u"""This browser view is used to return the torrent seeders for the video
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
