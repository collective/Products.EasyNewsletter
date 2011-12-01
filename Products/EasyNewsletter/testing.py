from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2
from zope.configuration import xmlconfig


class EasyNewsletter(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import Products.EasyNewsletter
        xmlconfig.file('configure.zcml',
                       Products.EasyNewsletter,
                       context=configurationContext)

        # Install product and call its initialize() function
        z2.installProduct(app, 'Products.EasyNewsletter')

        # Note: you can skip this if Products.EasyNewsletter is not a Zope 2-style
        # product, i.e. it is not in the Products.* namespace and it
        # does not have a <five:registerPackage /> directive in its
        # configure.zcml.

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'Products.EasyNewsletter:default')

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'Products.EasyNewsletter')

        # Note: Again, you can skip this if Products.EasyNewsletter is not a Zope
        # 2-style product


EASYNEWSLETTER_FIXTURE = EasyNewsletter()

EASYNEWSLETTER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(EASYNEWSLETTER_FIXTURE, ), name="EasyNewsletter:Integration")

EASYNEWSLETTER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(EASYNEWSLETTER_FIXTURE, ), name="EasyNewsletter:Functional")
