# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from App.Common import package_home
from plone import api
from plone.app.testing import login, logout, setRoles, TEST_USER_ID, TEST_USER_NAME
from plone.testing.z2 import Browser
from Products.CMFPlone.tests.utils import MockMailHost
from Products.CMFPlone.utils import safe_unicode
from Products.EasyNewsletter.config import IS_PLONE_5
from Products.EasyNewsletter.interfaces import IENLRegistrationTool
from Products.EasyNewsletter.testing import (
    PRODUCTS_EASYNEWSLETTER_FUNCTIONAL_TESTING,
    PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING,
)
from Products.EasyNewsletter.tests.base import parsed_payloads_from_msg
from Products.EasyNewsletter.utils.mail import get_portal_mail_settings
from Products.MailHost.interfaces import IMailHost
from zope.component import getMultiAdapter, getSiteManager, getUtility

import unittest


GLOBALS = globals()
TESTS_HOME = package_home(GLOBALS)


if IS_PLONE_5:
    from plone.registry.interfaces import IRegistry
    from Products.CMFPlone.interfaces.controlpanel import IMailSchema


class RegistrationIntegrationTests(unittest.TestCase):
    layer = PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal_url = self.portal.portal_url()
        # create EasyNewsletter instance and add some subscribers
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.portal_workflow.setDefaultChain(
            "simple_publication_workflow",
        )
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Newsletter', 'enl1', title=u"ENL 1")
        self.newsletter = self.portal.get('enl1')
        self.newsletter.senderEmail = "newsletter@acme.com"
        self.newsletter.senderName = "ACME newsletter"
        self.newsletter.testEmail = "test@acme.com"
        self.mail_settings = get_portal_mail_settings()
        # Set up a mock mailhost
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost('MailHost')
        self.portal.MailHost.smtp_host = 'localhost'
        registry = getUtility(IRegistry)
        self.mail_settings = registry.forInterface(
            IMailSchema, prefix='plone')
        self.mail_settings.email_from_address = "portal@plone.test"
        self.mail_settings.smtp_host = u"localhost"
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)
        # We need to fake a valid mail setup
        self.mailhost = self.portal.MailHost
        self.enl_reg_tool = getUtility(
            IENLRegistrationTool, 'enl_registration_tool')

    def test_register_subscriber(self):
        self.assertSequenceEqual(self.mailhost.messages, [])
        self.portal.REQUEST.form.update({
            'newsletter': '/enl1',
            'salutation': u'mr',
            'firstname': 'Max',
            'name': 'Mustermann',
            'subscriber': 'max@example.com',
        })
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST),
            name="register-subscriber")
        view.__call__()
        self.assertEqual(len(self.mailhost.messages), 1)
        self.assertTrue(self.mailhost.messages[0])
        msg = safe_unicode(self.mailhost.messages[0])
        parsed_payloads = parsed_payloads_from_msg(msg)
        self.assertIn('To: max@example.com', msg)
        self.assertIn('From: portal@plone.test', msg)
        self.assertIn('confirm-subscriber?hkey=', safe_unicode(parsed_payloads['text/plain']))

        enl_reg_entry = self.enl_reg_tool.values()[0]
        self.assertEqual(
            enl_reg_entry.firstname,
            "Max",
        )
        self.assertTrue(enl_reg_entry.id)
        self.assertEqual(
            enl_reg_entry.lastname,
            "Mustermann",
        )
        self.assertEqual(
            enl_reg_entry.name_prefix,
            "",
        )
        self.assertEqual(
            enl_reg_entry.nl_language,
            "en",
        )
        self.assertEqual(
            enl_reg_entry.organization,
            "",
        )
        self.assertEqual(
            enl_reg_entry.path_to_easynewsletter,
            "enl1",
        )
        self.assertEqual(
            enl_reg_entry.salutation,
            "mr",
        )
        self.assertEqual(
            enl_reg_entry.subscriber,
            "max@example.com",
        )

    def test_confirm_subscriber(self):
        self.portal.REQUEST.form.update({
            'newsletter': '/enl1',
            'salutation': u'mr',
            'firstname': 'Max',
            'name': 'Mustermann',
            'subscriber': 'max@example.com',
            'organization': 'Musterfirma',
            'name_prefix': 'Dr.',
        })
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST),
            name="register-subscriber")
        view.__call__()

        enl_reg_entry = self.enl_reg_tool.values()[0]
        self.portal.REQUEST.form.update({
            'hkey': enl_reg_entry.id,
        })
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST),
            name="confirm-subscriber")
        view.__call__()
        catalog = self.portal.portal_catalog
        query = {'portal_type': 'Newsletter Subscriber'}
        results = catalog(query)
        self.assertTrue(len(results) == 1)
        subscriber = results[0].getObject()
        self.assertEqual(
            subscriber.firstname,
            "Max",
        )
        self.assertEqual(
            subscriber.lastname,
            "Mustermann",
        )
        self.assertEqual(
            subscriber.name_prefix,
            "Dr.",
        )
        self.assertEqual(
            subscriber.organization,
            "Musterfirma",
        )
        self.assertEqual(
            subscriber.salutation,
            "mr",
        )
        self.assertEqual(
            subscriber.title,
            "max@example.com - Dr. Max Mustermann",
        )

        # check that anonymous can't access the subscriber object
        subscriber_uid = subscriber.UID()
        logout()
        # Unauthorized gets raised in > 5.1
        # with self.assertRaises(Unauthorized):
        try:
            subscriber_obj = api.content.get(UID=subscriber_uid)
        except Unauthorized:
            pass
        else:
            # in Plone < 5.2 subscriber_obj has to be None:
            self.assertFalse(subscriber_obj)
        login(self.portal, TEST_USER_NAME)


class RegistrationFunctionalTests(unittest.TestCase):

    layer = PRODUCTS_EASYNEWSLETTER_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(self.portal)
        self.browser.handleErrors = False
        self.mail_settings = get_portal_mail_settings()
        self.mail_settings.email_from_address = "portal@plone.test"
        # Set up a mock mailhost
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost('MailHost')
        self.portal.MailHost.smtp_host = 'localhost'
        self.portal.MailHost.email_from_address = 'portal@plone.test'
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)
        # We need to fake a valid mail setup

        # create EasyNewsletter instance and add some subscribers
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        # self.portal.portal_workflow.setDefaultChain(
        #     "simple_publication_workflow",
        # )
        self.portal.invokeFactory('Newsletter', 'enl1', title=u"ENL 1")
        self.newsletter = self.portal.get('enl1')
        self.newsletter.senderEmail = "newsletter@acme.com"
        self.newsletter.senderName = "ACME newsletter"
        self.newsletter.testEmail = "test@acme.com"

        # Commit so that the test browser sees these changes
        import transaction as zt
        zt.commit()

    def test_registration_portlet(self):
        self.browser.open(self.newsletter.absolute_url())

        # self.assertTrue(
        #     u"You have been subscribed." in self.browser.contents,
        #     'There should be a portal message!')
        # self.assertTrue(
        #     subscriber1_id not in self.newsletter.objectIds(),
        #     'Subscriber should be delete now!')
