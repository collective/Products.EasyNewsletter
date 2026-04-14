import unittest

import transaction
from plone import api
from plone.app.testing import TEST_USER_ID, setRoles
from z3c.relationfield.relation import RelationValue
from zope.component import getMultiAdapter, getUtility
from zope.intid.interfaces import IIntIds

from Products.EasyNewsletter.testing import (
    PRODUCTS_EASYNEWSLETTER_FUNCTIONAL_TESTING,
)


class DailyIssueHasContentTest(unittest.TestCase):
    layer = PRODUCTS_EASYNEWSLETTER_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.portal.invokeFactory("Folder", "news-folder")
        self.folder = self.portal["news-folder"]

        self.newsletter = api.content.create(
            type="Newsletter",
            id="nl",
            container=self.portal,
            title="My Newsletter",
        )
        self.newsletter.sender_email = "newsletter@example.com"
        self.newsletter.sender_name = "Tester"
        self.newsletter.test_email = "test@example.com"

        self.collection = api.content.create(
            type="Collection",
            id="news-collection",
            container=self.folder,
            title="News Collection",
        )
        self.collection.setQuery(
            [
                {
                    "i": "portal_type",
                    "o": "plone.app.querystring.operation.selection.is",
                    "v": ["News Item"],
                }
            ]
        )
        transaction.commit()

        intids = getUtility(IIntIds)
        self.newsletter.content_aggregation_sources = [
            RelationValue(intids.getId(self.collection))
        ]

        self.view = getMultiAdapter(
            (self.newsletter, self.request), name="daily-issue"
        )

    def _create_news(self, count):
        for idx in range(count):
            api.content.create(
                type="News Item",
                id="news-{:02d}".format(idx),
                container=self.folder,
                title="News {}".format(idx),
            )

    def test_has_content_empty(self):
        self.assertFalse(self.view.has_content())

    def test_has_content_with_single_item(self):
        self._create_news(1)
        self.assertTrue(self.view.has_content())

    def test_has_content_with_many_items(self):
        # queryCatalog() defaults to batch=True with b_size=30. For collections
        # that contain more than 30 items has_content() would silently cap the
        # count at 30 — and in combination with a sort_limit can even lead to
        # a result count of 0 while the collection's own view still lists the
        # items. See https://github.com/collective/Products.EasyNewsletter
        self._create_news(50)
        count = self.view.has_content()
        self.assertEqual(count, 50)

    def test_has_content_with_broken_relation(self):
        # A deleted collection must not break has_content().
        self.newsletter.content_aggregation_sources.append(
            RelationValue(987654321)
        )
        self._create_news(1)
        self.assertTrue(self.view.has_content())


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
