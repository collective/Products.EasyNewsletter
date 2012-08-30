# -*- coding: utf-8 -*-
import unittest2 as unittest
from Products.CMFCore.utils import getToolByName
from plone.app.testing import TEST_USER_ID, setRoles

from Products.EasyNewsletter.interfaces import IENLIssue
from Products.EasyNewsletter.testing import EASYNEWSLETTER_INTEGRATION_TESTING

from zope.component import getMultiAdapter

from zope.component import getSiteManager
from Products.CMFPlone.tests.utils import MockMailHost
from Products.MailHost.interfaces import IMailHost

from Acquisition import aq_base


class DailyIssueTestCase(unittest.TestCase):
    """Test case sending a daily Newsletter issue"""

    layer = EASYNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.catalog = getToolByName(self.portal, "portal_catalog")
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        #creating test objects: folder, news, newsletter and subscriber
        self.portal.invokeFactory("Folder", "testfolder")
        self.folder = self.portal["testfolder"]
        self.folder.invokeFactory("News Item", "news01")

        self.folder.invokeFactory("EasyNewsletter", "daily-news")
        self.newsletter = self.folder["daily-news"]
        self.newsletter.setTitle("Daily News")

        criteria = self.newsletter.addCriterion("portal_type",
                                                "ATSimpleStringCriterion")
        criteria.setValue("News Item")

        self.newsletter.invokeFactory("ENLSubscriber", "subscriber01")
        self.view = getMultiAdapter((self.newsletter, self.layer["request"]),
                                    name="daily-issue")

        #setting a Mock mailhost
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost("MailHost")
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)

        self.portal.email_from_address = "noreply@plone.org"

    def tearDown(self):
        self.portal.MailHost = self.portal._original_MailHost
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(self.portal._original_MailHost),
                           provided=IMailHost)

    def test_create_new_issue(self):
        issues = self.catalog(object_provides=IENLIssue.__identifier__,
                              path="/".join(self.newsletter.getPhysicalPath()))
        self.assertEqual(len(issues), 0)

        self.view.create_issue()
        issues = self.catalog(object_provides=IENLIssue.__identifier__,
                              path="/".join(self.newsletter.getPhysicalPath()))

        self.assertEqual(len(issues), 1)
        self.assertEqual(self.view.issue.Title(), "Daily News")

    def test_empty_issue(self):
        self.folder.manage_delObjects(["news01"])
        self.view.create_issue()
        issues = self.catalog(object_provides=IENLIssue.__identifier__,
                              path="/".join(self.newsletter.getPhysicalPath()))
        self.assertFalse(issues)

    def test_send_issue(self):
        self.assertTrue(self.view.create_issue())
        self.view.send()
        self.assertEqual(len(self.portal.MailHost.messages), 1)

    def test_do_not_send_a_empty_issue(self):
        self.folder.manage_delObjects(["news01"])
        self.view.create_issue()
        self.view.send()
        self.assertEqual(len(self.portal.MailHost.messages), 0)

    def test_do_not_send_same_issue_twice(self):
        self.view.render()
        self.assertFalse(self.view.create_issue())
        self.assertFalse(self.view.send())


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
