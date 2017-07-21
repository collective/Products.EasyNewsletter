# -*- coding: utf-8 -*-
from App.Common import package_home
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFPlone.tests.utils import MockMailHost
from Products.EasyNewsletter.config import IS_PLONE_5
from Products.EasyNewsletter.interfaces import IBeforePersonalizationEvent
from Products.EasyNewsletter.interfaces import IIssueDataFetcher
from Products.EasyNewsletter.testing import EASYNEWSLETTER_FUNCTIONAL_TESTING
from Products.EasyNewsletter.utils.mail import get_portal_mail_settings
from Products.MailHost.interfaces import IMailHost
from zope.component import getGlobalSiteManager
from zope.component import getSiteManager
from zope.component import getUtility
from zope.component import provideHandler

import unittest


GLOBALS = globals()
TESTS_HOME = package_home(GLOBALS)


if IS_PLONE_5:
    from plone.registry.interfaces import IRegistry
    from Products.CMFPlone.interfaces.controlpanel import IMailSchema


class IssuedatafetcherIntegrationTests(unittest.TestCase):
    layer = EASYNEWSLETTER_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal_url = self.portal.portal_url()
        # create EasyNewsletter instance and add some subscribers
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('EasyNewsletter', 'enl1', title=u"ENL 1")
        self.newsletter = self.portal.get('enl1')
        self.newsletter.senderEmail = "newsletter@acme.com"
        self.newsletter.senderName = "ACME newsletter"
        self.newsletter.testEmail = "test@acme.com"
        self.mail_settings = get_portal_mail_settings()
        # Set up a mock mailhost
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost('MailHost')
        self.portal.MailHost.smtp_host = 'localhost'
        if not IS_PLONE_5:  # BBB
            self.portal.email_from_address = "portal@plone.test"
        else:
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
        self.newsletter.invokeFactory(
            "ENLIssue",
            id="issue")
        self.newsletter.issue.title = \
            "This is a very long newsletter issue title with special "\
            "characters such as äüö. Will this really work?"

    def test_before_personalization_filter(self):
        def _personalize(event):
            edc = event.data['context']
            event.data['html'] = event.data['html'].replace('PHP', 'Python')
            edc['SUBSCRIBER_SALUTATION'] = 'Dear Ms. Jane Doe'
        provideHandler(_personalize, [IBeforePersonalizationEvent])
        try:
            receiver = {
                'email': 'john@example.com',
                'fullname': 'John Doe',
                'firstname': 'John',
                'lastname': 'Doe',
                'salutation': 'Dear Mr.',
                'nl_language': 'de'
            }
            html = '''
            <h1>PHP ist toll!</h1>
            {{SUBSCRIBER_SALUTATION}}
            '''
            issue_data_fetcher = IIssueDataFetcher(self.newsletter.issue)
            issue_data = issue_data_fetcher._personalize(receiver, html)
            self.assertIn('Dear Ms. Jane Doe', issue_data)
        finally:
            getGlobalSiteManager().unregisterHandler(
                _personalize, [IBeforePersonalizationEvent])
