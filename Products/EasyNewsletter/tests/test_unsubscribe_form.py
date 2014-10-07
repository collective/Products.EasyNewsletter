# -*- coding: utf-8 -*-
from App.Common import package_home
from Products.CMFPlone.tests.utils import MockMailHost
from Products.EasyNewsletter.testing import EASYNEWSLETTER_FUNCTIONAL_TESTING
from Products.EasyNewsletter.testing import EASYNEWSLETTER_INTEGRATION_TESTING
from Products.MailHost.interfaces import IMailHost
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.testing.z2 import Browser
from zope.component import getMultiAdapter
from zope.component import getSiteManager
import unittest2 as unittest


GLOBALS = globals()
TESTS_HOME = package_home(GLOBALS)


class UnsubscribeFormIntegrationTests(unittest.TestCase):

    layer = EASYNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()

        # create EasyNewsletter instance and add some subscribers
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        self.portal.invokeFactory('EasyNewsletter', 'enl1', title=u"ENL 1")
        self.newsletter = self.portal.get('enl1')
        self.newsletter.invokeFactory(
            'ENLSubscriber', 'subscriber1', salutation=u"mr",
            fullname='Max Mustermann', email='max@example.com')
        self.newsletter.invokeFactory(
            'ENLSubscriber', 'subscriber2', salutation=u"mr",
            fullname='Maxima Musterfrau', email='maxima@example.com')
        self.newsletter.senderEmail = "newsletter@acme.com"
        self.newsletter.senderName = "ACME newsletter"
        self.newsletter.testEmail = "test@acme.com"

        # Set up a mock mailhost
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost('MailHost')
        self.portal.MailHost.smtp_host = 'localhost'
        self.portal.MailHost.email_from_address = 'portal@plone.test'
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)
        # We need to fake a valid mail setup
        self.portal.email_from_address = "portal@plone.test"
        self.mailhost = self.portal.MailHost

    def test_submit_unsubscribe_form(self):
        self.assertSequenceEqual(self.mailhost.messages, [])
        self.portal.REQUEST.form.update({
            'subscriber': u'max@example.com',
            'test': 'submit',
        })
        view = getMultiAdapter(
            (self.newsletter, self.portal.REQUEST),
            name="unsubscribe_form")
        view = view.__of__(self.portal)
        view.__call__()

        self.assertEqual(len(self.mailhost.messages), 1)
        self.assertTrue(self.mailhost.messages[0])
        msg = str(self.mailhost.messages[0])
        self.assertIn('To: max@example.com', msg)
        self.assertIn('From: portal@plone.test', msg)


class UnsubscribeFormFunctionalTests(unittest.TestCase):

    layer = EASYNEWSLETTER_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        self.unsubscribe_form_url = self.portal_url + '/enl1/unsubscribe_form'
        self.unsubscribe_view_url = self.portal_url + '/enl1/unsubscribe'
        self.browser = Browser(self.portal)
        self.browser.handleErrors = False

        # create EasyNewsletter instance and add some subscribers
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('EasyNewsletter', 'enl1', title=u"ENL 1")
        self.newsletter = self.portal.get('enl1')
        self.newsletter.senderEmail = "newsletter@acme.com"
        self.newsletter.senderName = "ACME newsletter"
        self.newsletter.testEmail = "test@acme.com"
        self.newsletter.invokeFactory(
            'ENLSubscriber', 'subscriber1', salutation=u"mr",
            fullname='Max Mustermann', email='max@example.com')
        self.newsletter.invokeFactory(
            'ENLSubscriber', 'subscriber2', salutation=u"mr",
            fullname='Maxima Musterfrau', email='maxima@example.com')

        # Commit so that the test browser sees these changes
        import transaction as zt
        zt.commit()

    def test_render_unsubscribe_form(self):
        self.browser.open(self.unsubscribe_form_url)
        self.assertTrue(u"unsubscribe_form" in self.browser.contents)

    def test_unsubscribe_view(self):
        subscriber1_id = self.newsletter.subscriber1.id
        self.browser.open(
            self.unsubscribe_view_url + '?subscriber=' +
            self.newsletter.subscriber1.UID())
        self.assertTrue(
            u"You have been unsubscribed." in self.browser.contents,
            'There should be a portal message!')
        self.assertTrue(
            subscriber1_id not in self.newsletter.objectIds(),
            'Subscriber should be delete now!')
