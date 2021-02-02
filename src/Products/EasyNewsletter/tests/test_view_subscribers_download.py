# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles, TEST_USER_ID
from Products.EasyNewsletter.testing import (
    PRODUCTS_EASYNEWSLETTER_FUNCTIONAL_TESTING,
    PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING,
)
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError

import six
import unittest


class ViewsIntegrationTest(unittest.TestCase):

    layer = PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.newsletter = api.content.create(
            container=self.portal, type="Newsletter", id="newsletter"
        )
        self.newsletter.subscriber = api.content.create(
            container=self.newsletter,
            type="Newsletter Subscriber",
            id="newsletter_subscriber",
            email="jane@example.com",
            lastname="Doe",
            firstname="Jane",
            organization="Doe Cörp",
        )

    def test_subscribers_download_is_registered(self):
        view = getMultiAdapter(
            (self.newsletter, self.portal.REQUEST), name="subscribers-download"
        )
        self.assertTrue(view.__name__ == "subscribers-download")

    def test_subscribers_download_not_matching_interface(self):
        with self.assertRaises(ComponentLookupError):
            getMultiAdapter(
                (self.portal, self.portal.REQUEST), name="subscribers-download"
            )

    def test_subscribers_download_call(self):
        view = getMultiAdapter(
            (self.newsletter, self.portal.REQUEST), name="subscribers-download"
        )
        result = view()
        self.assertEqual(
            b"salutation,name_prefix,firstname,lastname,email,organization\n,,Jane,Doe,jane@example.com,Doe C\xc3\xb6rp\n",
            result.replace(b'\r', b''),
        )
        self.assertTrue(
            isinstance(result, six.binary_type), "result must be binary_type!"
        )


class ViewsFunctionalTest(unittest.TestCase):

    layer = PRODUCTS_EASYNEWSLETTER_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
