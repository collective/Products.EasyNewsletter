import unittest

from plone import api
from plone.app.testing import TEST_USER_ID, setRoles
from zope.component import getMultiAdapter

from Products.EasyNewsletter.testing import (
    PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING,
)


class FakeContentListingObject:
    """Mimics plone.app.contentlisting's CatalogContentListingObject.

    Unlike a raw catalog brain (where ``Title``/``Description`` are metadata
    attributes) these are methods, and the object carries no Zope security
    declarations. The helper accessors must cope with both shapes.
    """

    def __init__(self, obj):
        self._obj = obj

    def Title(self):
        return self._obj.Title()

    def Description(self):
        return self._obj.Description()

    def getObject(self):
        return self._obj

    def getURL(self):
        return self._obj.absolute_url()


class HelperViewIntegrationTest(unittest.TestCase):
    layer = PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.doc = api.content.create(
            container=self.portal,
            type="Document",
            id="a-doc",
            title="A Document",
            description="A short description.",
        )
        self.helper = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name="enl_helpers"
        )
        self.brain = api.content.find(UID=self.doc.UID())[0]
        self.listing = FakeContentListingObject(self.doc)

    def test_get_title_from_brain(self):
        self.assertEqual(self.helper.get_title(self.brain), "A Document")

    def test_get_title_from_contentlisting_object(self):
        # Regression: contentlisting wrappers expose Title() as a method and
        # are not restricted-accessible, which used to raise NotFound in the
        # skin templates. The trusted accessor must normalize both shapes.
        self.assertEqual(self.helper.get_title(self.listing), "A Document")

    def test_get_description_from_brain(self):
        self.assertEqual(
            self.helper.get_description(self.brain), "A short description."
        )

    def test_get_description_from_contentlisting_object(self):
        self.assertEqual(
            self.helper.get_description(self.listing), "A short description."
        )

    def test_get_object_from_brain(self):
        self.assertEqual(self.helper.get_object(self.brain), self.doc)

    def test_get_object_from_contentlisting_object(self):
        self.assertEqual(self.helper.get_object(self.listing), self.doc)

    def test_get_object_url_from_contentlisting_object(self):
        self.assertEqual(
            self.helper.get_object_url(self.listing), self.doc.absolute_url()
        )

    def test_accessors_tolerate_none(self):
        self.assertEqual(self.helper.get_title(None), "")
        self.assertEqual(self.helper.get_description(None), "")
        self.assertIsNone(self.helper.get_object(None))
        self.assertIsNone(self.helper.get_object_url(None))
