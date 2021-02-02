# -*- coding: utf-8 -*-
from plone.app.testing import setRoles, TEST_USER_ID
from Products.EasyNewsletter.config import IS_PLONE_5
from Products.EasyNewsletter.testing import PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING

import unittest


if IS_PLONE_5:
    from zope.component import getUtility
    from plone.registry.interfaces import IRegistry
    from Products.CMFPlone.interfaces import INavigationSchema, ISearchSchema


class EasyNewsletterSetupTests(unittest.TestCase):

    layer = PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']
        registry = getUtility(IRegistry)
        self.search_settings = registry.forInterface(
            ISearchSchema, prefix="plone")
        self.nav_settings = registry.forInterface(
            INavigationSchema, prefix='plone')

    def test_newsletter_factory(self):
        self.folder.invokeFactory("Newsletter", "newsletter")
        self.assertEqual(
            'Newsletter', self.folder.newsletter.portal_type)

    def test_catalog(self):
        indexes = self.portal.portal_catalog.indexes()
        self.assertEqual('email' in indexes, True)

    def test_newsletter_subtypes_in_meta_types_not_to_list(self):
        self.assertTrue(
            'Newsletter' in self.nav_settings.displayed_types)
        self.assertFalse('Newsletter Issue' in self.nav_settings.displayed_types)
        self.assertFalse(
            'Newsletter Subscriber' in self.nav_settings.displayed_types)

    def test_newsletter_subtypes_in_types_not_searched(self):
        self.assertTrue(
            'Newsletter Subscriber' in self.search_settings.types_not_searched)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
