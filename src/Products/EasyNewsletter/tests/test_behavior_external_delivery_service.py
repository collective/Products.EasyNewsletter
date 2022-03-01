# -*- coding: utf-8 -*-

import unittest

from plone.app.testing import TEST_USER_ID, setRoles
from plone.behavior.interfaces import IBehavior
from zope.component import getUtility

from Products.EasyNewsletter.behaviors.external_delivery_service import (
    IExternalDeliveryServiceMarker,
)
from Products.EasyNewsletter.testing import PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING


class ExternalDeliveryServiceIntegrationTest(unittest.TestCase):

    layer = PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_behavior_external_delivery_service(self):
        behavior = getUtility(
            IBehavior, "Products.EasyNewsletter.external_delivery_service"
        )
        self.assertEqual(
            behavior.marker,
            IExternalDeliveryServiceMarker,
        )
