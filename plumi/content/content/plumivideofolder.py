"""Definition of the Plumi Video Folder content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from plumi.content import plumiMessageFactory as _
from plumi.content.interfaces import IPlumiVideoFolder
from plumi.content.config import PROJECTNAME

PlumiVideoFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

PlumiVideoFolderSchema['title'].storage = atapi.AnnotationStorage()
PlumiVideoFolderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    PlumiVideoFolderSchema,
    folderish=True,
    moveDiscussion=False
)

class PlumiVideoFolder(folder.ATFolder):
    """Folder for video content"""
    implements(IPlumiVideoFolder)

    meta_type = "Plumi Video Folder"
    schema = PlumiVideoFolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(PlumiVideoFolder, PROJECTNAME)
