# -*- coding: utf-8 -*-
import unittest
from datetime import datetime, timedelta

from App.Common import package_home
from plone import api
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, login, setRoles

from Products.EasyNewsletter.interfaces import IIssueDataFetcher
from Products.EasyNewsletter.testing import PRODUCTS_EASYNEWSLETTER_FUNCTIONAL_TESTING

GLOBALS = globals()
TESTS_HOME = package_home(GLOBALS)


class PlaceholderIntegrationTests(unittest.TestCase):
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
            title="ENL 1",
            sneder_email="newsletter@acme.com",
            sender_name="ACME newsletter",
            test_email="test@acme.com",
        )
        api.content.create(
            container=self.newsletter,
            type="Newsletter Issue",
            id="issue",
            title="This is a very long newsletter issue title with special "
            "characters such as äüö. Will this really work?",
        )

    def test_placeholder_month_year(self):
        receiver = {
            "email": "john@example.com",
            "fullname": "John Doe",
            "firstname": "John",
            "lastname": "Doe",
            "salutation": "Dear Mr.",
        }
        html = """
        <h1>Plone ist toll!</h1>
        {{ SUBSCRIBER_SALUTATION }}
        {{ month }}/{{ year }}
        """
        now = datetime.now()
        effective_date = now + timedelta(2)
        self.newsletter.issue.effective_date = effective_date
        self.assertNotEqual(
            self.newsletter.issue.modified(), self.newsletter.issue.effective()
        )
        issue_data_fetcher = IIssueDataFetcher(self.newsletter.issue)
        issue_data = issue_data_fetcher.personalize(receiver, html)
        self.assertIn(
            "{0}/{1}".format(
                self.newsletter.issue.effective().month(),
                self.newsletter.issue.effective().year(),
            ),
            issue_data,
        )

    def test_placeholder_calendar_week(self):
        receiver = {
            "email": "john@example.com",
            "fullname": "John Doe",
            "firstname": "John",
            "lastname": "Doe",
            "salutation": "Dear Mr.",
        }
        html = """
        <h1>Plone ist toll!</h1>
        {{ SUBSCRIBER_SALUTATION }}
        {{ calendar_week }}
        """
        now = datetime.now()
        effective_date = now + timedelta(2)
        self.newsletter.issue.effective_date = effective_date
        self.assertNotEqual(
            self.newsletter.issue.modified(), self.newsletter.issue.effective()
        )
        issue_data_fetcher = IIssueDataFetcher(self.newsletter.issue)
        issue_data = issue_data_fetcher.personalize(receiver, html)
        self.assertIn(self.newsletter.issue.effective().strftime("%V"), issue_data)
