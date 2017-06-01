# -*- coding: utf-8 -*-
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from zope.configuration import xmlconfig

import pkg_resources

try:
    pkg_resources.get_distribution('plone.app.contenttypes')
except pkg_resources.DistributionNotFound:
    HAS_PACT = False
else:
    HAS_PACT = True


class EasyNewsletter(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        if HAS_PACT:
            z2.installProduct(app, 'plone.app.contenttypes')
        # Load ZCML
        import Products.EasyNewsletter
        xmlconfig.file('configure.zcml',
                       Products.EasyNewsletter,
                       context=configurationContext)

        # Install product and call its initialize() function
        z2.installProduct(app, 'Products.EasyNewsletter')

    def setUpPloneSite(self, portal):
        if HAS_PACT:
            applyProfile(portal, 'plone.app.contenttypes:default')
        # Install into Plone site using portal_setup
        applyProfile(portal, 'Products.EasyNewsletter:default')
        applyProfile(portal, 'Products.EasyNewsletter:install-base')

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'Products.EasyNewsletter')


EASYNEWSLETTER_FIXTURE = EasyNewsletter()

EASYNEWSLETTER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(EASYNEWSLETTER_FIXTURE, ),
    name="EasyNewsletter:Integration"
)

EASYNEWSLETTER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(EASYNEWSLETTER_FIXTURE, ),
    name="EasyNewsletter:Functional"
)
