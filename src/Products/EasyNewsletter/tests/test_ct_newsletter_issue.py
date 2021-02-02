# -*- coding: utf-8 -*-
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles, TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from Products.EasyNewsletter.content.newsletter_issue import INewsletterIssue
from Products.EasyNewsletter.testing import PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING
from zope.component import createObject, queryUtility

import unittest


class NewsletterIssueIntegrationTest(unittest.TestCase):

    layer = PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            'Newsletter',
            self.portal,
            'newsletter',
            title='Parent container',
        )
        self.parent = self.portal[parent_id]

    def test_ct_newsletter_issue_schema(self):
        fti = queryUtility(IDexterityFTI, name='Newsletter Issue')
        schema = fti.lookupSchema()
        self.assertEqual(INewsletterIssue, schema)

    def test_ct_newsletter_issue_fti(self):
        fti = queryUtility(IDexterityFTI, name='Newsletter Issue')
        self.assertTrue(fti)

    def test_ct_newsletter_issue_factory(self):
        fti = queryUtility(IDexterityFTI, name='Newsletter Issue')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            INewsletterIssue.providedBy(obj),
            u'INewsletterIssue not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_newsletter_issue_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='Newsletter Issue',
            id='newsletter_issue',
        )

        self.assertTrue(
            INewsletterIssue.providedBy(obj),
            u'INewsletterIssue not provided by {0}!'.format(
                obj.id,
            ),
        )

        self.assertIn('newsletter_issue', self.parent.objectIds())
        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('newsletter_issue', self.parent.objectIds())

    def test_ct_newsletter_issue_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Newsletter Issue')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )

    def test_ct_newsletter_issue_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Newsletter Issue')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'newsletter_issue_id',
            title='Newsletter Issue container',
        )
        self.parent = self.portal[parent_id]
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type='Document',
                title='My Content',
            )
