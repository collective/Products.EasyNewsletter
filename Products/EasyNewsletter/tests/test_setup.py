# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.EasyNewsletter.config import IS_PLONE_5
from Products.EasyNewsletter.testing import EASYNEWSLETTER_INTEGRATION_TESTING
import unittest


if IS_PLONE_5:
    from zope.component import getUtility
    from plone.registry.interfaces import IRegistry
    from Products.CMFPlone.interfaces import INavigationSchema, ISearchSchema


class EasyNewsletterSetupTests(unittest.TestCase):

    layer = EASYNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']
        if not IS_PLONE_5:  # BBB
            self.properties = self.portal.portal_properties
        else:
            registry = getUtility(IRegistry)
            self.search_settings = registry.forInterface(
                ISearchSchema, prefix="plone")
            self.nav_settings = registry.forInterface(
                INavigationSchema, prefix='plone')

    def test_newsletter_factory(self):
        self.folder.invokeFactory("EasyNewsletter", "newsletter")
        self.assertEqual(
            'EasyNewsletter', self.folder.newsletter.portal_type)

    def test_catalog(self):
        indexes = self.portal.portal_catalog.indexes()
        self.assertEqual('email' in indexes, True)

    def test_newsletter_subtypes_in_meta_types_not_to_list(self):
        if not IS_PLONE_5:  # BBB
            # Hide newsletter subtypes from navigation
            self.assertTrue(
                self.properties.navtree_properties.hasProperty(
                    'metaTypesNotToList'))
            metaTypesNotToList = \
                self.properties.navtree_properties.metaTypesNotToList
            self.assertTrue(
                'ENLIssue' in metaTypesNotToList)
            self.assertTrue(
                'ENLSubscriber' in metaTypesNotToList)
            self.assertTrue(
                'ENLTemplate' in metaTypesNotToList)
        else:
            self.assertTrue(
                'EasyNewsletter' in self.nav_settings.displayed_types)
            self.assertFalse('ENLIssue' in self.nav_settings.displayed_types)
            self.assertFalse(
                'ENLSubscriber' in self.nav_settings.displayed_types)
            self.assertFalse(
                'ENLTemplate' in self.nav_settings.displayed_types)

    def test_newsletter_subtypes_in_types_not_searched(self):
        if not IS_PLONE_5:  # BBB
            site_props = self.properties.site_properties
            self.assertTrue(
                site_props.hasProperty(
                    'types_not_searched'))
            types_not_searched = site_props.types_not_searched
            self.assertTrue(
                'ENLSubscriber' in types_not_searched)
        else:
            self.assertTrue(
                'ENLSubscriber' in self.search_settings.types_not_searched)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
