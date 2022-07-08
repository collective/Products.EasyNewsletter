# -*- coding: utf-8 -*-

from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.EasyNewsletter import _
from Products.EasyNewsletter.testing import PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.interfaces import IVocabularyTokenized

import unittest


class PloneUsersIntegrationTest(unittest.TestCase):

    layer = PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.jane = api.user.create(
            email="jane@plone.org", username="jane", properties={"fullname": "Jane Doe"}
        )
        self.john = api.user.create(
            email="john@plone.org", username="john", properties={"fullname": "John Doe"}
        )

    def test_vocab_plone_users(self):
        vocab_name = "Products.EasyNewsletter.PloneUsers"
        factory = getUtility(IVocabularyFactory, vocab_name)
        self.assertTrue(IVocabularyFactory.providedBy(factory))

        vocabulary = factory(self.portal)
        self.assertTrue(IVocabularyTokenized.providedBy(vocabulary))
        self.assertEqual(
            vocabulary.getTerm(self.jane.getId()).title, _("Jane Doe - jane@plone.org")
        )
