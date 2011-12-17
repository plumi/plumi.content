"""Test setup for integration and functional tests.

When we import PloneTestCase and then call setupPloneSite(), all of
Plone's products are loaded, and a Plone site will be created. This
happens at module level, which makes it faster to run each test, but
slows down test runner startup.
"""
    
from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Products.CMFCore.utils import getToolByName

from ZODB.FileStorage.FileStorage import FileStorage
from ZODB.MappingStorage import MappingStorage
from ZODB.blob import BlobStorage
from tempfile import mkdtemp
from plone.app.blob.tests import bbb


# When ZopeTestCase configures Zope, it will *not* auto-load products
# in Products/. Instead, we have to use a statement such as:
#   ztc.installProduct('SimpleAttachment')
# This does *not* apply to products in eggs and Python packages (i.e.
# not in the Products.*) namespace. For that, see below.
# All of Plone's products are already set up by PloneTestCase.

ptc.setupPloneSite(id='plone')

@onsetup
def setup_product():
    """Set up the package and its dependencies.

    The @onsetup decorator causes the execution of this body to be
    deferred until the setup of the Plone site testing layer. We could
    have created our own layer, but this is the easiest way for Plone
    integration tests.
    """
    ztc.installProduct('Archetypes')
    ztc.installProduct('MimetypesRegistry')
    ztc.installProduct('PortalTransforms') 
    # to support tests for translated vocabularies
    ztc.installProduct('PloneLanguageTool')
    # Load the ZCML configuration for the example.tests package.
    # This can of course use <include /> to include other packages.

    import Products.ATVocabularyManager
    import plumi.content
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', Products.ATVocabularyManager)
    zcml.load_config('configure.zcml', plumi.content)        
    fiveconfigure.debug_mode = False
        
    ztc.installPackage('ATVocabularyManager')
    ztc.installPackage('plumi.content')

# The order here is important: We first call the (deferred) function
# which installs the products we need for this product. Then, we let
# PloneTestCase set up this product on installation.

setup_product()
ptc.installProduct('ATVocabularyManager')
ptc.installProduct('plumi.content')
ptc.setupPloneSite(products=('plumi.content',))     
    
    
class TestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If
    necessary, we can put common utility or setup code in here. This
    applies to unit test cases.
    """

class FunctionalTestCase(ptc.FunctionalTestCase):
    """We use this class for functional integration tests that use
    doctest syntax. Again, we can put basic common utility or setup
    code in here.
    """
    layer = bbb.plone

    def afterSetUp(self):
        self.loginAsPortalOwner()
        roles = ('Member', 'Contributor')
        self.portal.portal_membership.addMember('contributor',
                                                'secret',
                                                roles, [])
