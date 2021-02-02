# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PLONE_FIXTURE,
    PloneSandboxLayer,
)
from plone.testing import z2
from Products.EasyNewsletter.tests.base import enable_behavior

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
        self.loadZCML(package=Products.EasyNewsletter)

        # Install product and call its initialize() function
        z2.installProduct(app, 'Products.EasyNewsletter')

    def setUpPloneSite(self, portal):
        if HAS_PACT:
            applyProfile(portal, 'plone.app.contenttypes:default')
        # Install into Plone site using portal_setup
        applyProfile(portal, 'Products.EasyNewsletter:default')
        # applyProfile(portal, 'Products.EasyNewsletter:install-base')
        enable_behavior(
            "Newsletter", "Products.EasyNewsletter.plone_user_group_recipients"
        )
        enable_behavior(
            "Newsletter Issue", "Products.EasyNewsletter.plone_user_group_recipients"
        )

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'Products.EasyNewsletter')


EASYNEWSLETTER_FIXTURE = EasyNewsletter()

PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(EASYNEWSLETTER_FIXTURE, ),
    name="EasyNewsletter:Integration"
)

PRODUCTS_EASYNEWSLETTER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(EASYNEWSLETTER_FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE, z2.ZSERVER_FIXTURE),
    name="EasyNewsletter:Functional"
)
