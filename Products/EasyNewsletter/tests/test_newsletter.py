# -*- coding: utf-8 -*-
import unittest2 as unittest

#from zope.component import createObject
from zope.component import getMultiAdapter
#from zope.component import queryUtility
from zope.component import getSiteManager

from Products.MailHost.interfaces import IMailHost
from Products.CMFPlone.tests.utils import MockMailHost

from Products.EasyNewsletter.testing import \
    EASYNEWSLETTER_INTEGRATION_TESTING

from plone.app.testing import TEST_USER_ID, setRoles
from plone.app.testing import TEST_USER_NAME, login

from Products.EasyNewsletter.interfaces import IEasyNewsletter, IENLIssue


class EasyNewsletterTests(unittest.TestCase):

    layer = EASYNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']
        self.portal = self.layer['portal']
        self.folder.invokeFactory("EasyNewsletter", "newsletter")
        self.newsletter = self.folder.newsletter
        self.newsletter.senderEmail = "newsletter@acme.com"
        self.newsletter.senderName = "ACME newsletter"
        self.newsletter.testEmail = "test@acme.com"
        # Set up a mock mailhost
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost('MailHost')
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)
        # We need to fake a valid mail setup
        self.portal.email_from_address = "portal@plone.test"
        self.mailhost = self.portal.MailHost

    def test_create_newsletter(self):
        self.failUnless(IEasyNewsletter.providedBy(self.newsletter))

    def test_create_issue(self):
        self.newsletter.invokeFactory(
            "ENLIssue",
            id="issue",
            title="Issue 1")
        self.failUnless(IENLIssue.providedBy(self.newsletter.issue))

    def test_send_test_issue(self):
        self.newsletter.invokeFactory(
            "ENLIssue",
            id="issue")
        self.newsletter.issue.title="This is a very long newsletter issue title with special characters such as äüö. Will this really work?"
        self.portal.REQUEST.form.update({
            'sender_name': self.newsletter.senderName,
            'sender_email': self.newsletter.senderEmail,
            'test_receiver': self.newsletter.testEmail,
            'subject': self.newsletter.issue.title,
            'test': 'submit',
        })
        view = getMultiAdapter(
            (self.newsletter.issue, self.portal.REQUEST),
            name="send-issue")
        view = view.__of__(self.portal)

        view.send_issue()

        self.assertEqual(len(self.mailhost.messages), 1)
        self.assertTrue(self.mailhost.messages[0])
        msg = str(self.mailhost.messages[0])
        self.assertTrue('To: <test@acme.com>' in msg)
        self.assertTrue('From: ACME newsletter <newsletter@acme.com>' in msg)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

#raceback (innermost last):
#  Module ZPublisher.Publish, line 127, in publish
#  Module ZPublisher.mapply, line 77, in mapply
#  Module Products.PDBDebugMode.runcall, line 70, in pdb_runcall
#  Module ZPublisher.Publish, line 47, in call_object
#  Module Products.EasyNewsletter.browser.issue, line 23, in send_issue
#  Module Products.EasyNewsletter.content.ENLIssue, line 366, in send
#  Module email.header, line 176, in __init__
#  Module email.header, line 260, in append
#UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 75: ordinal not in range(128)
#*** SyntaxError: invalid syntax (<stdin>, line 1)
#> /usr/lib/python2.6/email/header.py(260)append()
#-> ustr = unicode(s, incodec, errors)
