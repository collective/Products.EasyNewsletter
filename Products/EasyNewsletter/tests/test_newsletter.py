# -*- coding: utf-8 -*-
from App.Common import package_home
from Products.CMFPlone.tests.utils import MockMailHost
from Products.EasyNewsletter.interfaces import IENLIssue
from Products.EasyNewsletter.interfaces import IEasyNewsletter
from Products.EasyNewsletter.testing import EASYNEWSLETTER_INTEGRATION_TESTING
from Products.MailHost.interfaces import IMailHost
from Products.TinyMCE.interfaces.utility import ITinyMCE
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from zope.component import getMultiAdapter
from zope.component import getSiteManager
from zope.component import queryUtility
import os
import unittest2 as unittest

GLOBALS = globals()
TESTS_HOME = package_home(GLOBALS)


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
        # image for image testing
        self.folder.invokeFactory("Image", "image")
        self.image = self.folder.image
        img1 = open(os.path.join(TESTS_HOME, 'img1.png'), 'rb').read()
        self.image.edit(image=img1)

    def sendSampleMessage(self, body):
        self.assertSequenceEqual(self.mailhost.messages, [])
        self.newsletter.invokeFactory(
            "ENLIssue",
            id="issue")
        self.newsletter.issue.title = "with image"
        self.portal.REQUEST.form.update({
            'sender_name': self.newsletter.senderName,
            'sender_email': self.newsletter.senderEmail,
            'test_receiver': self.newsletter.testEmail,
            'subject': self.newsletter.issue.title,
            'test': 'submit',
        })
        self.newsletter.issue.setText(body, mimetype='text/html')
        view = getMultiAdapter(
            (self.newsletter.issue, self.portal.REQUEST),
            name="send-issue")
        view = view.__of__(self.portal)

        view.send_issue()

        self.assertEqual(len(self.mailhost.messages), 1)
        self.assertTrue(self.mailhost.messages[0])
        return str(self.mailhost.messages[0])

    def test_create_newsletter(self):
        self.assertTrue(IEasyNewsletter.providedBy(self.newsletter))

    def test_create_issue(self):
        self.newsletter.invokeFactory(
            "ENLIssue",
            id="issue",
            title="Issue 1")
        self.assertTrue(IENLIssue.providedBy(self.newsletter.issue))

    def test_send_test_issue(self):
        self.newsletter.invokeFactory(
            "ENLIssue",
            id="issue")
        self.newsletter.issue.title = \
            "This is a very long newsletter issue title with special "\
            "characters such as äüö. Will this really work?"
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
        self.assertIn('To: <test@acme.com>', msg)
        self.assertIn('From: ACME newsletter <newsletter@acme.com>', msg)

    def test_send_test_issue_with_image(self):
        body = '<img src="../../image"/>'
        msg = self.sendSampleMessage(body)

        self.assertIn('<img src=3D"cid:image_1"', msg)
        self.assertIn('Content-ID: <image_1>\nContent-Type: image/png;', msg)

    def test_send_test_issue_with_scale_image(self):
        body = '<img src="../../image/@@images/image/thumb"/>'
        msg = self.sendSampleMessage(body)

        self.assertIn('<img src=3D"cid:image_1"', msg)
        self.assertIn('Content-ID: <image_1>\nContent-Type: image/png;', msg)

    def test_send_test_issue_with_resolveuid_image(self):
        # for plone < 4.2 we need to ensure turn on to resolveuid links
        tinymce = queryUtility(ITinyMCE)
        tinymce.link_using_uids = True

        body = '<img src="../../resolveuid/%s"/>' % self.image.UID()
        msg = self.sendSampleMessage(body)

        self.assertNotIn('resolveuid', msg)
        self.assertIn('<img src=3D"cid:image_1"', msg)
        self.assertIn('Content-ID: <image_1>\nContent-Type: image/png;', msg)

    def test_send_test_issue_with_resolveuid_scale_image(self):
        # for plone < 4.2 we need to ensure turn on to resolveuid links
        tinymce = queryUtility(ITinyMCE)
        tinymce.link_using_uids = True

        body = '<img src="../../resolveuid/%s/@@images/image/thumb"/>' % \
            self.image.UID()
        msg = self.sendSampleMessage(body)

        self.assertNotIn('resolveuid', msg)
        self.assertIn('<img src=3D"cid:image_1"', msg)
        self.assertIn('Content-ID: <image_1>\nContent-Type: image/png;', msg)

    def test_mailonly_filter_in_issue_public_view(self):
        self.newsletter.invokeFactory(
            "ENLIssue",
            id="issue")
        self.newsletter.issue.title = "Test Newsletter Issue"
        self.newsletter.issue.setText(
            "<h1>This is the newsletter body!</h1><div class=\"mailonly\">"
            "This test should only visible in mails not in public view!</div>")
        view = getMultiAdapter(
            (self.newsletter.issue, self.portal.REQUEST),
            name="get-public-body")
        view = view.__of__(self.portal)
        view_result = view()

        self.assertTrue(
            'mailonly' not in view_result,
            'get-public-body view contains mailonly elements,'
            ' this should filtert out!')

    def test_permission(self):
        setRoles(self.portal, TEST_USER_ID, ['Editor'])
        self.portal.REQUEST.set('ACTUAL_URL', 'http://nohost')
        self.newsletter.invokeFactory(
            "ENLIssue",
            id="issue")
        self.newsletter.issue.title = "Test Newsletter Issue"
        self.newsletter.issue.setText("<h1>This is the newsletter body!")

        view = self.newsletter.restrictedTraverse("enl_drafts_view")
        view_result = view()
        self.assertIn('test-folder/newsletter/issue', view_result)

        view = self.newsletter.restrictedTraverse("issue/send-issue-form")
        view_result = view()

        self.assertIn('Test Newsletter', view_result)

        view = self.newsletter.restrictedTraverse("issue/send-issue")
        view_result = view()

        self.assertIn('issue', view_result)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
