# -*- coding: utf-8 -*-

from plone.app.testing import setRoles, TEST_USER_ID
from plone.behavior.interfaces import IBehavior
from Products.EasyNewsletter.behaviors.plone_user_group_recipients import (
    IPloneUserGroupRecipientsMarker,
)
from Products.EasyNewsletter.testing import PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING
from zope.component import getUtility

import unittest


class PloneUserGroupRecipientsIntegrationTest(unittest.TestCase):

    layer = PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_behavior_plone_user_group_recipients(self):
        behavior = getUtility(IBehavior, 'Products.EasyNewsletter.plone_user_group_recipients')
        self.assertEqual(
            behavior.marker,
            IPloneUserGroupRecipientsMarker,
        )
