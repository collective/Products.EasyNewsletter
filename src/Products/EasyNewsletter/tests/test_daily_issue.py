# -*- coding: utf-8 -*-
from Acquisition import aq_base
from plone import api
from plone.app.testing import setRoles, TEST_USER_ID
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.tests.utils import MockMailHost
from Products.EasyNewsletter.content.newsletter_issue import INewsletterIssue
from Products.EasyNewsletter.testing import PRODUCTS_EASYNEWSLETTER_FUNCTIONAL_TESTING
from Products.EasyNewsletter.utils.mail import get_portal_mail_settings
from Products.MailHost.interfaces import IMailHost
from z3c.relationfield.relation import RelationValue
from zExceptions import BadRequest
from zope.component import getMultiAdapter, getSiteManager, getUtility
from zope.intid.interfaces import IIntIds

import transaction
import unittest


class DailyIssueBaseTestCase(unittest.TestCase):
    """Test case sending a daily Newsletter issue"""

    layer = PRODUCTS_EASYNEWSLETTER_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.catalog = getToolByName(self.portal, "portal_catalog")
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        # creating test objects: folder, news, newsletter and subscriber
        self.portal.invokeFactory("Folder", "testfolder")
        self.folder = self.portal["testfolder"]
        self.folder.invokeFactory("News Item", "news01")

        self.folder.invokeFactory("Newsletter", "daily-news")
        self.newsletter = self.folder["daily-news"]
        self.newsletter.title = u"Daily News"
        # XXX check if we could ovaid this by using defaults from site settings
        self.newsletter.sender_email = u"newsletter@acme.com"
        self.newsletter.sender_name = u"ACME newsletter"
        self.newsletter.test_email = u"test@acme.com"

        news_collection = api.content.create(
            type="Collection",
            id="news-collection",
            title=u"News Collection",
            container=self.folder,
        )
        query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.selection.is",
                "v": ["News Item"],
            }
        ]
        news_collection.setQuery(query)
        news_collection.aggregation_template = "aggregation_generic_listing"
        transaction.commit()
        intids = getUtility(IIntIds)
        to_id = intids.getId(news_collection)
        self.newsletter.content_aggregation_sources = [RelationValue(to_id)]

        api.content.create(
            type="Newsletter Subscriber",
            id="subscriber01",
            container=self.newsletter,
            email=u"jane@example.com",
        )
        self.view = getMultiAdapter(
            (self.newsletter, self.layer["request"]), name="daily-issue"
        )

        self.mail_settings = get_portal_mail_settings()
        self.mail_settings.email_from_address = "noreply@plone.org"
        # setting a Mock mailhost
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost("MailHost")
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)

    def tearDown(self):
        self.portal.MailHost = self.portal._original_MailHost
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(self.portal._original_MailHost), provided=IMailHost)


class DailyIssueContent(DailyIssueBaseTestCase):
    def test_create_new_issue(self):
        issues = self.catalog(
            object_provides=INewsletterIssue.__identifier__,
            path="/".join(self.newsletter.getPhysicalPath()),
        )
        self.assertEqual(len(issues), 0)
        self.assertFalse(self.view.already_sent())
        self.view.create_issue()

        issues = self.catalog(
            object_provides=INewsletterIssue.__identifier__,
            path="/".join(self.newsletter.getPhysicalPath()),
        )

        self.assertTrue(self.view.already_sent())
        self.assertEqual(len(issues), 1)
        self.assertEqual(self.view.issue.title, "Daily News")

    def test_empty_issue(self):
        self.assertTrue(self.view.has_content())
        self.folder.manage_delObjects(["news01"])
        self.assertFalse(self.view.has_content())

    def test_send_issue(self):
        try:
            self.view.create_issue()
        except Exception:
            self.fail("Couldn't create issue!")

        self.view.send()
        self.assertEqual(len(self.portal.MailHost.messages), 1)


class DailyIssueMethodGET(DailyIssueBaseTestCase):
    def setUp(self):
        self.layer["request"]["REQUEST_METHOD"] = "GET"
        DailyIssueBaseTestCase.setUp(self)

    def test_get_with_an_empty_issue(self):
        self.folder.manage_delObjects(["news01"])
        self.view()
        self.assertEqual(self.view.request.response.getStatus(), 204)

    def test_get_with_a_non_empty_issue(self):
        self.view()
        self.assertEqual(self.view.request.response.getStatus(), 100)

    def test_get_an_alredy_sent_issue(self):
        self.view.create_issue()
        self.view()
        self.assertEqual(self.view.request.response.getStatus(), 200)


class DailyIssueMethodPOST(DailyIssueBaseTestCase):
    def setUp(self):
        self.layer["request"]["REQUEST_METHOD"] = "POST"
        DailyIssueBaseTestCase.setUp(self)

    def test_do_not_create_or_send_an_empty_issue(self):
        self.folder.manage_delObjects(["news01"])
        self.view()
        issues = self.catalog(
            object_provides=INewsletterIssue.__identifier__,
            path="/".join(self.newsletter.getPhysicalPath()),
        )
        self.assertFalse(issues)
        self.assertEqual(self.view.request.response.getStatus(), 204)
        self.assertEqual(len(self.portal.MailHost.messages), 0)

    def test_send_issue_and_check_http_status(self):
        self.view()
        self.assertEqual(self.view.request.response.getStatus(), 200)
        self.assertEqual(len(self.portal.MailHost.messages), 1)

    def test_do_not_send_same_issue_twice(self):
        self.view()  # 200 OK
        self.assertEqual(self.view.request.response.getStatus(), 200)
        self.assertRaises(BadRequest, self.view.create_issue)
        self.view()  # 409 Already Sent
        self.assertEqual(self.view.request.response.getStatus(), 409)


class TriggerDailyIssueMethodGET(DailyIssueBaseTestCase):
    def setUp(self):
        self.layer["request"]["REQUEST_METHOD"] = "GET"
        DailyIssueBaseTestCase.setUp(self)
        self.view = getMultiAdapter(
            (self.newsletter, self.layer["request"]), name="trigger-daily-issue"
        )

    def test_send_issue_and_check_http_status(self):
        self.view()
        self.assertEqual(self.view.request.response.getStatus(), 200)
        self.assertEqual(len(self.portal.MailHost.messages), 1)


class DailyIssueMethodOtherThanGETorPOST(DailyIssueBaseTestCase):
    def setUp(self):
        self.layer["request"]["REQUEST_METHOD"] = "FOOBAR"
        DailyIssueBaseTestCase.setUp(self)

    def test_trying_another_method_on_view(self):
        self.view()
        self.assertEqual(self.view.request.response.getStatus(), 405)
        self.assertEqual(self.view.request.response.getHeader("Allow"), "GET, POST")


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
