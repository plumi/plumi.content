import os
import tempfile
import shutil
import json

from five import grok

from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName

from plumi.content import plumiMessageFactory as _

IMAGE_MIMETYPES = ['image/jpeg', 'image/gif', 'image/png']

grok.templatedir('templates')

class PlumiUploader(grok.View):
    """ Handler for the upload process.
    """
    grok.context(IFolderish)
    grok.require('cmf.AddPortalContent')
    grok.name('plumi_uploader')

    files = []

    def __call__(self, *args, **kwargs):
        if hasattr(self.request, "REQUEST_METHOD"):
            if self.request["REQUEST_METHOD"] == "POST":
                pm = getToolByName(self.context,'portal_membership')
                userId = pm.getAuthenticatedMember().id
                session_path = tempfile.gettempdir() + '/' + 'plumitmp/' + userId
                shutil.rmtree(session_path, ignore_errors=True)
                if getattr(self.request, "video_file", None):
                    uploaded_file = self.request['video_file']
                    os.makedirs(session_path)
                    file = open(session_path + '/' + uploaded_file.filename, 'w')
                    file.write(uploaded_file.read())
                    uploaded_file.close()
                    print file.name
                    file.close() 

                return json.dumps([{}])
            
        return super(PlumiUploader, self).__call__(*args, **kwargs)

