from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from plumi.content import plumiMessageFactory as _

from plumivideo import IPlumiBaseVideo


class IPlumiExternalVideo(IPlumiBaseVideo):
    """Plumi Video content"""
