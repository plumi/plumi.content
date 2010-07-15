from Products.Five.browser import BrowserView



class RSSView(BrowserView):

    def items(self):
        return self.context.getFolderContents(contentFilter={"portal_type":"PlumiVideo", "review_state":['published', 'featured'], 'sort_on': 'effective', 'sort_order': 'reverse'})
