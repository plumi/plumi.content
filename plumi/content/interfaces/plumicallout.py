from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from plumi.content import contentMessageFactory as _

class IPlumiCallOut(Interface):
    """Call out for help with production of video content"""
    
    # -*- schema definition goes here -*-
