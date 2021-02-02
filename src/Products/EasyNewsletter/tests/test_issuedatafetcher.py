# -*- coding: utf-8 -*-
from App.Common import package_home
from plone import api
from plone.app.testing import login, setRoles, TEST_USER_ID, TEST_USER_NAME
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.CMFPlone.tests.utils import MockMailHost
from Products.EasyNewsletter.interfaces import (
    IBeforePersonalizationEvent,
    IIssueDataFetcher,
)
from Products.EasyNewsletter.testing import PRODUCTS_EASYNEWSLETTER_FUNCTIONAL_TESTING
from Products.EasyNewsletter.utils.mail import get_portal_mail_settings
from Products.MailHost.interfaces import IMailHost
from zope.component import (
    getGlobalSiteManager,
    getSiteManager,
    getUtility,
    provideHandler,
)

import unittest


GLOBALS = globals()
TESTS_HOME = package_home(GLOBALS)


class IssuedatafetcherIntegrationTests(unittest.TestCase):
    layer = PRODUCTS_EASYNEWSLETTER_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.portal_url()
        # create EasyNewsletter instance and add some subscribers
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)
        self.newsletter = api.content.create(
            container=self.portal,
            type="Newsletter",
            id="enl1",
            title=u"ENL 1",
            sneder_email=u"newsletter@acme.com",
            sender_name=u"ACME newsletter",
            test_email=u"test@acme.com",
        )
        self.mail_settings = get_portal_mail_settings()
        # Set up a mock mailhost
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost("MailHost")
        self.portal.MailHost.smtp_host = "localhost"
        registry = getUtility(IRegistry)
        self.mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        self.mail_settings.email_from_address = "portal@plone.test"
        self.mail_settings.smtp_host = u"localhost"
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)
        # We need to fake a valid mail setup
        self.mailhost = self.portal.MailHost
        api.content.create(
            container=self.newsletter,
            type="Newsletter Issue",
            id="issue",
            title=u"This is a very long newsletter issue title with special "
            u"characters such as äüö. Will this really work?",
        )

    def test_before_personalization_filter(self):
        def personalize(event):
            edc = event.data["context"]
            event.data["html"] = event.data["html"].replace("PHP", "Python")
            edc["SUBSCRIBER_SALUTATION"] = "Dear Ms. Jane Doe"
        provideHandler(personalize, [IBeforePersonalizationEvent])

        try:
            receiver = {
                "email": "john@example.com",
                "fullname": "John Doe",
                "firstname": "John",
                "lastname": "Doe",
                "salutation": "Dear Mr.",
                # "nl_language": "de",
            }
            html = """
            <h1>PHP ist toll!</h1>
            {{SUBSCRIBER_SALUTATION}}
            """
            issue_data_fetcher = IIssueDataFetcher(self.newsletter.issue)
            issue_data = issue_data_fetcher.personalize(receiver, html)
            self.assertIn("Dear Ms. Jane Doe", issue_data)
        finally:
            getGlobalSiteManager().unregisterHandler(
                personalize, [IBeforePersonalizationEvent]
            )

    def test_fetching_issue_data(self):

        receiver = {
            "email": "john@example.com",
            "fullname": "John Doe",
            "firstname": "John",
            "lastname": "Doe",
            "salutation": "Dear Mr.",
        }
        html = """
        <h1></h1>
        {{SUBSCRIBER_SALUTATION}}
        """
        issue_data_fetcher = IIssueDataFetcher(self.newsletter.issue)
        issue_data = issue_data_fetcher.personalize(receiver, html)
        self.assertIn("Dear Mr. John Doe", issue_data)
