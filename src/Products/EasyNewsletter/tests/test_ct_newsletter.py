# -*- coding: utf-8 -*-
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles, TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from Products.EasyNewsletter.content.newsletter import INewsletter
from Products.EasyNewsletter.testing import PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING
from zope.component import createObject, queryUtility

import unittest


class NewsletterIntegrationTest(unittest.TestCase):

    layer = PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_ct_newsletter_schema(self):
        fti = queryUtility(IDexterityFTI, name='Newsletter')
        schema = fti.lookupSchema()
        self.assertEqual(INewsletter, schema)

    def test_ct_newsletter_fti(self):
        fti = queryUtility(IDexterityFTI, name='Newsletter')
        self.assertTrue(fti)

    def test_ct_newsletter_factory(self):
        fti = queryUtility(IDexterityFTI, name='Newsletter')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            INewsletter.providedBy(obj),
            u'INewsletter not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_newsletter_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='Newsletter',
            id='newsletter',
        )

        self.assertTrue(
            INewsletter.providedBy(obj),
            u'INewsletter not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('newsletter', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('newsletter', parent.objectIds())

    def test_ct_newsletter_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Newsletter')
        self.assertTrue(
            fti.global_allow,
            u'{0} is not globally addable!'.format(fti.id)
        )

    def test_ct_newsletter_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Newsletter')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'newsletter_id',
            title='Newsletter container',
        )
        parent = self.portal[parent_id]
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=parent,
                type='Document',
                title='My Content',
            )
