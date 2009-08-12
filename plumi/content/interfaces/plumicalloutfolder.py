from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from plumi.content import plumiMessageFactory as _

class IPlumiCalloutFolder(Interface):
    """Folder for call outs"""
    
    # -*- schema definition goes here -*-
