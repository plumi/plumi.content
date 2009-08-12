from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from plumi.content import plumiMessageFactory as _

class IPlumiVideoFolder(Interface):
    """Folder for video content"""
    
    # -*- schema definition goes here -*-
