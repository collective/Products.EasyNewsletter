# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles, TEST_USER_ID
from Products.EasyNewsletter.testing import (
    PRODUCTS_EASYNEWSLETTER_FUNCTIONAL_TESTING,
    PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING,
)
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError

import unittest


class ViewsIntegrationTest(unittest.TestCase):

    layer = PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.newsletter = api.content.create(container=self.portal, type='Newsletter', id='newsletter')
        self.issue = api.content.create(container=self.newsletter, type='Newsletter Issue', id='issue')

    def test_send_issue_is_registered(self):
        view = getMultiAdapter(
            (self.issue, self.portal.REQUEST),
            name='send-issue'
        )
        self.assertTrue(view.__name__ == 'send-issue')

    def test_send_issue_not_matching_interface(self):
        with self.assertRaises(ComponentLookupError):
            getMultiAdapter(
                (self.portal, self.portal.REQUEST),
                name='send-issue'
            )


class ViewsFunctionalTest(unittest.TestCase):

    layer = PRODUCTS_EASYNEWSLETTER_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
