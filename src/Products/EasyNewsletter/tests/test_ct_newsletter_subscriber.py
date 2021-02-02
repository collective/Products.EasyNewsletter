# -*- coding: utf-8 -*-

from plone import api
from plone.app.testing import setRoles, TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from Products.EasyNewsletter.content.newsletter_subscriber import INewsletterSubscriber
from Products.EasyNewsletter.testing import PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING
from zope.component import createObject, queryUtility

import unittest


class NewsletterSubscriberIntegrationTest(unittest.TestCase):

    layer = PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            'Newsletter',
            self.portal,
            'parent_container',
            title='Parent container',
        )
        self.parent = self.portal[parent_id]

    def test_ct_newsletter_subscriber_schema(self):
        fti = queryUtility(IDexterityFTI, name='Newsletter Subscriber')
        schema = fti.lookupSchema()
        self.assertEqual(INewsletterSubscriber, schema)

    def test_ct_newsletter_subscriber_fti(self):
        fti = queryUtility(IDexterityFTI, name='Newsletter Subscriber')
        self.assertTrue(fti)

    def test_ct_newsletter_subscriber_factory(self):
        fti = queryUtility(IDexterityFTI, name='Newsletter Subscriber')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            INewsletterSubscriber.providedBy(obj),
            u'INewsletterSubscriber not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_newsletter_subscriber_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='Newsletter Subscriber',
            id='newsletter_subscriber',
        )

        self.assertTrue(
            INewsletterSubscriber.providedBy(obj),
            u'INewsletterSubscriber not provided by {0}!'.format(
                obj.id,
            ),
        )

        self.assertIn('newsletter_subscriber', self.parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('newsletter_subscriber', self.parent.objectIds())

    def test_ct_newsletter_subscriber_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Newsletter Subscriber')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )
