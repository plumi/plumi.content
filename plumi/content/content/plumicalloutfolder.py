"""Definition of the Plumi Callout Folder content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from plumi.content import plumiMessageFactory as _
from plumi.content.interfaces import IPlumiCalloutFolder
from plumi.content.config import PROJECTNAME

PlumiCalloutFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

PlumiCalloutFolderSchema['title'].storage = atapi.AnnotationStorage()
PlumiCalloutFolderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    PlumiCalloutFolderSchema,
    folderish=True,
    moveDiscussion=False
)

class PlumiCalloutFolder(folder.ATFolder):
    """Folder for call outs"""
    implements(IPlumiCalloutFolder)

    meta_type = "Plumi Callout Folder"
    schema = PlumiCalloutFolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(PlumiCalloutFolder, PROJECTNAME)
