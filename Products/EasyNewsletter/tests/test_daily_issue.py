# -*- coding: utf-8 -*-
from Acquisition import aq_base
from plone import api
from plone.uuid.interfaces import IUUID
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.tests.utils import MockMailHost
from Products.EasyNewsletter.interfaces import IENLIssue
from Products.EasyNewsletter.testing import EASYNEWSLETTER_FUNCTIONAL_TESTING
from Products.EasyNewsletter.utils.mail import get_portal_mail_settings
# from Products.EasyNewsletter.config import IS_PLONE_5
from Products.MailHost.interfaces import IMailHost
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.component import getSiteManager
# from zope.component import getUtility
# from plone.dexterity.interfaces import IDexterityFTI
import unittest


class DailyIssueBaseTestCase(unittest.TestCase):
    """Test case sending a daily Newsletter issue"""

    layer = EASYNEWSLETTER_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.catalog = getToolByName(self.portal, "portal_catalog")
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        # creating test objects: folder, news, newsletter and subscriber
        self.portal.invokeFactory("Folder", "testfolder")
        self.folder = self.portal["testfolder"]
        self.folder.invokeFactory("News Item", "news01")

        self.folder.invokeFactory("EasyNewsletter", "daily-news")
        self.newsletter = self.folder["daily-news"]
        self.newsletter.setTitle("Daily News")

        # if IS_PLONE_5:
        #     # make sure that Collections have the referenceable behavior:
        #     fti = getUtility(IDexterityFTI, name='Collection')
        #     referenceable = u'plone.app.referenceablebehavior.referenceable.IReferenceable'  # noqa
        #     behaviors = list(fti.behaviors)
        #     if referenceable not in behaviors:
        #         behaviors.append(referenceable)
        #         fti.behaviors = tuple(behaviors)

        news_collection = api.content.create(
            type="Collection",
            id='news-collection',
            title=u'News Collection',
            container=self.folder)
        query = [{
            'i': 'portal_type',
            'o': 'plone.app.querystring.operation.selection.is',
            'v': ['News Item'],
        }]
        news_collection.setQuery(query)
        self.newsletter.setContentAggregationSources(IUUID(news_collection))

        self.newsletter.invokeFactory("ENLSubscriber", "subscriber01")
        self.view = getMultiAdapter(
            (self.newsletter, self.layer["request"]),
            name="daily-issue"
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
        sm.registerUtility(
            aq_base(self.portal._original_MailHost),
            provided=IMailHost
        )


class DailyIssueContent(DailyIssueBaseTestCase):
    def test_create_new_issue(self):
        issues = self.catalog(
            object_provides=IENLIssue.__identifier__,
            path="/".join(self.newsletter.getPhysicalPath())
        )
        self.assertEqual(len(issues), 0)
        self.assertFalse(self.view.already_sent())
        self.view.create_issue()
        # try:
        #     self.view.create_issue()
        # except Exception, e:
        #     import pdb; pdb.set_trace()
        #     self.fail("Couldn't create an issue! (%s)" % e)

        issues = self.catalog(
            object_provides=IENLIssue.__identifier__,
            path="/".join(self.newsletter.getPhysicalPath())
        )

        self.assertTrue(self.view.already_sent())
        self.assertEqual(len(issues), 1)
        self.assertEqual(self.view.issue.Title(), "Daily News")

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
            object_provides=IENLIssue.__identifier__,
            path="/".join(self.newsletter.getPhysicalPath())
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


class DailyIssueMethodOtherThanGETorPOST(DailyIssueBaseTestCase):

    def setUp(self):
        self.layer["request"]["REQUEST_METHOD"] = "FOOBAR"
        DailyIssueBaseTestCase.setUp(self)

    def test_trying_another_method_on_view(self):
        self.view()
        self.assertEqual(self.view.request.response.getStatus(), 405)
        self.assertEqual(
            self.view.request.response.getHeader("Allow"),
            "GET, POST"
        )


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
