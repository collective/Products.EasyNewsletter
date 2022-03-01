# -*- coding: utf-8 -*-
import unittest

from plone.app.testing import TEST_USER_ID, setRoles
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory, IVocabularyTokenized

from Products.EasyNewsletter import _
from Products.EasyNewsletter.testing import PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING


class OutputTemplatesIntegrationTest(unittest.TestCase):

    layer = PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_vocab_output_templates(self):
        vocab_name = "Products.EasyNewsletter.OutputTemplates"
        factory = getUtility(IVocabularyFactory, vocab_name)
        self.assertTrue(IVocabularyFactory.providedBy(factory))

        vocabulary = factory(self.portal)
        self.assertTrue(IVocabularyTokenized.providedBy(vocabulary))
        self.assertEqual(
            vocabulary.getTerm("output_default").title,
            _("Default output template"),
        )
