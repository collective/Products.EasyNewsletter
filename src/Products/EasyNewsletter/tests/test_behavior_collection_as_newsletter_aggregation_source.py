# -*- coding: utf-8 -*-

from plone.app.testing import setRoles, TEST_USER_ID
from plone.behavior.interfaces import IBehavior
from Products.EasyNewsletter.behaviors.collection_as_newsletter_aggregation_source import (
    ICollectionAsNewsletterAggregationSourceMarker,
)
from Products.EasyNewsletter.testing import PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING
from zope.component import getUtility

import unittest


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
            behavior.marker, ICollectionAsNewsletterAggregationSourceMarker,
        )
