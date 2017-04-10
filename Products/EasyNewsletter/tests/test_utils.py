# -*- coding: utf-8 -*-
from App.Common import package_home
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFPlone.tests.utils import MockMailHost
from Products.EasyNewsletter.utils.mail import get_portal_mail_settings
from Products.EasyNewsletter.testing import EASYNEWSLETTER_INTEGRATION_TESTING
from Products.EasyNewsletter.config import IS_PLONE_5
from Products.MailHost.interfaces import IMailHost
from zope.component import getSiteManager
from zope.component import getUtility

import unittest


if IS_PLONE_5:
    from plone.registry.interfaces import IRegistry
    from Products.CMFPlone.interfaces.controlpanel import IMailSchema

GLOBALS = globals()
TESTS_HOME = package_home(GLOBALS)


class UtilsIntegrationTests(unittest.TestCase):
    layer = EASYNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal_url = self.portal.portal_url()
        # create EasyNewsletter instance and add some subscribers
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost('MailHost')
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)
        self.mail_host = getUtility(IMailHost)

        if not IS_PLONE_5:  # BBB
            self.portal.email_from_address = "portal@plone.test"
            self.portal.email_from_name = u"Plone Master"
            self.mail_host.smtp_host = u"example.com"
            self.mail_host.smtp_port = 25
            self.mail_host.smtp_userid = u"portal@plone.test"
            self.mail_host.smtp_pass = u"Password"
        else:
            self.registry = getUtility(IRegistry)
            reg_mail = self.registry.forInterface(
                IMailSchema, prefix='plone')
            reg_mail.email_from_address = 'portal@plone.test'
            reg_mail.email_from_name = u'Plone Master'
            reg_mail.smtp_host = u'example.com'
            reg_mail.smtp_port = 25
            reg_mail.smtp_userid = u'portal@plone.test'
            reg_mail.smtp_pass = u'Password'

    def test_portal_mail_settings(self):
        settings = get_portal_mail_settings()
        self.assertEqual('portal@plone.test', settings.email_from_address)
        self.assertEqual(u'Plone Master', settings.email_from_name)
        self.assertEqual(u'example.com', settings.smtp_host)
        self.assertEqual(25, settings.smtp_port)
        self.assertEqual(u'portal@plone.test', settings.smtp_userid)
        self.assertEqual(u'Password', settings.smtp_pass)
