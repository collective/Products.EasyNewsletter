# -*- coding: utf-8 -*-

from App.Common import package_home
from plone import api
from plone.app.testing import login, logout, setRoles, TEST_USER_ID, TEST_USER_NAME
from plone.testing.z2 import Browser
from Products.CMFPlone.tests.utils import MockMailHost
from Products.CMFPlone.utils import safe_unicode
from Products.EasyNewsletter.config import IS_PLONE_5
from Products.EasyNewsletter.testing import (
    PRODUCTS_EASYNEWSLETTER_FUNCTIONAL_TESTING,
    PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING,
)
from Products.MailHost.interfaces import IMailHost
from zope.component import getMultiAdapter, getSiteManager, getUtility

import unittest


GLOBALS = globals()
TESTS_HOME = package_home(GLOBALS)

if IS_PLONE_5:
    from plone.registry.interfaces import IRegistry
    from Products.CMFPlone.interfaces.controlpanel import IMailSchema


class UnsubscribeFormIntegrationTests(unittest.TestCase):

    layer = PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

        # create EasyNewsletter instance and add some subscribers
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.portal.portal_workflow.setDefaultChain("simple_publication_workflow")
        login(self.portal, TEST_USER_NAME)
        registry = getUtility(IRegistry)
        self.mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        self.mail_settings.smtp_host = u"localhost"
        self.mail_settings.email_from_address = "portal@plone.test"

        self.newsletter = api.content.create(
            container=self.portal, type="Newsletter", title="ENL 1", id="enl1"
        )
        api.content.create(
            type="Newsletter Subscriber",
            container=self.newsletter,
            id="sub1",
            salutation="mr",
            firstname="Max",
            lastname="Mustermann",
            email="max@example.com",
        )
        api.content.create(
            type="Newsletter Subscriber",
            container=self.newsletter,
            id="sub2",
            salutation="mr",
            firstname="Maxima",
            lastname="Musterfrau",
            email="maxima@example.com",
        )
        self.newsletter.senderEmail = "newsletter@acme.com"
        self.newsletter.senderName = "ACME newsletter"
        self.newsletter.testEmail = "test@acme.com"

        # Set up a mock mailhost
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost("MailHost")
        self.portal.MailHost.smtp_host = "localhost"
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)
        # We need to fake a valid mail setup
        self.mailhost = self.portal.MailHost
        logout()

    def test_submit_unsubscribe_form(self):
        self.assertSequenceEqual(self.mailhost.messages, [])
        self.portal.REQUEST.form.update(
            {"subscriber": u"max@example.com", "test": "submit"}
        )
        view = getMultiAdapter(
            (self.newsletter, self.portal.REQUEST), name="unsubscribe-form"
        )
        view.__call__()
        self.assertEqual(len(self.mailhost.messages), 1)
        self.assertTrue(self.mailhost.messages[0])
        msg = safe_unicode(self.mailhost.messages[0])
        self.assertIn("To: max@example.com", msg)
        self.assertIn("From: portal@plone.test", msg)


class UnsubscribeFormFunctionalTests(unittest.TestCase):

    layer = PRODUCTS_EASYNEWSLETTER_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.unsubscribe_form_url = self.portal_url + "/enl1/unsubscribe-form"
        self.unsubscribe_view_url = self.portal_url + "/enl1/unsubscribe"
        self.browser = Browser(self.portal)
        self.browser.handleErrors = False

        # create EasyNewsletter instance and add some subscribers
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.portal.portal_workflow.setDefaultChain("simple_publication_workflow")
        self.dummy_page = api.content.create(
            type="Document", id="dummy_page", title=u"Dummy page", container=self.portal
        )
        self.newsletter = api.content.create(
            container=self.portal, type="Newsletter", title="ENL 1", id="enl1"
        )
        self.newsletter.senderEmail = "newsletter@acme.com"
        self.newsletter.senderName = "ACME newsletter"
        self.newsletter.testEmail = "test@acme.com"
        api.content.create(
            type="Newsletter Subscriber",
            container=self.newsletter,
            id="subscriber1",
            salutation="mr",
            firstname="Max",
            lastname="Mustermann",
            email="max@example.com",
        )
        api.content.create(
            type="Newsletter Subscriber",
            container=self.newsletter,
            id="subscriber2",
            salutation="mr",
            firstname="Maxima",
            lastname="Musterfrau",
            email="maxima@example.com",
        )

        # Commit so that the test browser sees these changes
        import transaction as zt

        zt.commit()
        logout()

    def test_render_unsubscribe_form(self):
        self.browser.open(self.unsubscribe_form_url)
        self.assertTrue(u"unsubscribe-form" in safe_unicode(self.browser.contents))

    def test_unsubscribe_view(self):
        subscriber1_id = self.newsletter.subscriber1.id
        self.browser.open(
            self.unsubscribe_view_url
            + "?subscriber="
            + self.newsletter.subscriber1.UID()
        )
        self.assertTrue(
            u"You have been unsubscribed." in safe_unicode(self.browser.contents),
            "There should be a portal message!",
        )
        self.assertTrue(
            subscriber1_id not in self.newsletter.objectIds(),
            "Subscriber should be delete now!",
        )

        self.browser.open(
            self.unsubscribe_view_url + "?subscriber=" + self.dummy_page.UID()
        )
        self.assertTrue(
            self.dummy_page.id in self.portal.objectIds(),
            "Dummy page should not be deleted by unsubscribe form!",
        )
