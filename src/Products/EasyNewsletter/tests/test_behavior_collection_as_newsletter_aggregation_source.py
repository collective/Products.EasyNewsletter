# -*- coding: utf-8 -*-

import unittest

from plone.app.testing import TEST_USER_ID, setRoles
from plone.behavior.interfaces import IBehavior
from zope.component import getUtility

from Products.EasyNewsletter.behaviors.collection_as_newsletter_aggregation_source import (
    ICollectionAsNewsletterAggregationSourceMarker,
)
from Products.EasyNewsletter.testing import PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING


class CollectionAsNewsletterAggregationSourceIntegrationTest(unittest.TestCase):

    layer = PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_behavior_collection_as_newsletter_aggregation_source(self):
        behavior = getUtility(
            IBehavior,
            "Products.EasyNewsletter.collection_as_newsletter_aggregation_source",
        )
        self.assertEqual(
            behavior.marker,
            ICollectionAsNewsletterAggregationSourceMarker,
        )
