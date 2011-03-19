from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.testing import z2, Layer
from plone.app.testing import ploneSite
from plone.app.testing import quickInstallProduct
from plone.app.testing import setRoles
from plone.app.testing.interfaces import TEST_USER_ID

class PlumiLayer(PloneSandboxLayer):
    default_bases = (PLONE_FIXTURE,)
    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plumi.content
        import Products.ATVocabularyManager
        self.loadZCML(package=plumi.content)
        self.loadZCML(package=Products.ATVocabularyManager)

        # Install product and call its initialize() function
        z2.installProduct(app, 'Products.ATVocabularyManager')        
        z2.installProduct(app, 'plumi.content')

        # Note: you can skip this if my.product is not a Zope 2-style
        # product, i.e. it is not in the Products.* namespace and it
        # does not have a <five:registerPackage /> directive in its
        # configure.zcml.

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup       
        self.applyProfile(portal, 'plumi.content:default')
        setRoles(portal, TEST_USER_ID, ['Contributor'])


    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'plumi.content')

PLUMI_FIXTURE = PlumiLayer()

PLUMI_INTEGRATION_TESTING = IntegrationTesting(bases=(PLUMI_FIXTURE,), name="PLumiFixture:Integration")
PLUMI_FUNCTIONAL_TESTING = FunctionalTesting(bases=(PLUMI_FIXTURE, z2.ZSERVER_FIXTURE), name="PlumiFixture:Functional")