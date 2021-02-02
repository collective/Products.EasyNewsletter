# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles, TEST_USER_ID
from Products.CMFPlone.utils import safe_encode, safe_unicode
from Products.EasyNewsletter.testing import (
    PRODUCTS_EASYNEWSLETTER_FUNCTIONAL_TESTING,
    PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING,
)
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError

import os
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

    def test_subscribers_upload_is_registered(self):
        view = getMultiAdapter(
            (self.newsletter, self.portal.REQUEST), name="subscribers-upload"
        )
        self.assertTrue(view.__name__ == "subscribers-upload")

    def test_subscribers_upload_not_matching_interface(self):
        with self.assertRaises(ComponentLookupError):
            getMultiAdapter(
                (self.portal, self.portal.REQUEST), name="subscribers-upload"
            )

    def test_subscribers_upload_create_subscribers(self):
        template = """salutation,name_prefix,firstname,lastname,email,organization
Ms,PhD,Jane,Doe,jane@example.com,Doe Cörp
Mr,PhD,John,Doe,john@example.com,Doe Cörp
"""
        filename = os.path.join(os.path.dirname(__file__), "easynewsletter-subscribers.csv")
        if six.PY2:
            with open(filename, "wb") as f:
                f.write(safe_encode(template))
        else:
            with open(filename, "w", newline="") as f:
                f.write(safe_unicode(template))
        if six.PY2:
            file = open(filename)
        else:
            file = open(filename, "rb")

        self.portal.REQUEST.form.update({
            'form.button.Import': 'submit',
            'csv_upload': file,
        })
        view = getMultiAdapter(
            (self.newsletter, self.portal.REQUEST), name="subscribers-upload"
        )
        self.assertTrue(view.__name__ == "subscribers-upload")
        view.create_subscribers()
        file.close()


class ViewsFunctionalTest(unittest.TestCase):

    layer = PRODUCTS_EASYNEWSLETTER_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
