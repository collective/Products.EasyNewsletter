# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from App.Common import package_home
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFPlone.tests.utils import MockMailHost
from Products.EasyNewsletter.config import IS_PLONE_4
from Products.EasyNewsletter.config import IS_PLONE_5
from Products.EasyNewsletter.interfaces import IBeforePersonalizationEvent
from Products.EasyNewsletter.interfaces import IEasyNewsletter
from Products.EasyNewsletter.interfaces import IENLIssue
from Products.EasyNewsletter.testing import EASYNEWSLETTER_FUNCTIONAL_TESTING
from Products.EasyNewsletter.utils.mail import get_portal_mail_settings
from Products.MailHost.interfaces import IMailHost
from zExceptions import Forbidden
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.component import getSiteManager
from zope.component import provideHandler
from zope.component import queryUtility
from zope.interface import Interface

import os
import pkg_resources
import transaction as zt
import unittest


try:
    pkg_resources.get_distribution('Products.TinyMCE')
except pkg_resources.DistributionNotFound:

    class ITinyMCE(Interface):
        pass

else:
    from Products.TinyMCE.interfaces.utility import ITinyMCE

GLOBALS = globals()
TESTS_HOME = package_home(GLOBALS)


def dummy_image(image=None):
    from plone.namedfile.file import NamedBlobImage
    # filename = open(os.path.join(TESTS_HOME, 'img1.png'), 'rb')
    filename = os.path.join(os.path.dirname(__file__), u'img1.png')
    if not IS_PLONE_5:  # BBB
        image.edit(image=open(filename, 'r').read())
    else:
        return NamedBlobImage(
            data=open(filename, 'r').read(),
            filename=filename
        )


class EasyNewsletterTests(unittest.TestCase):
    layer = EASYNEWSLETTER_FUNCTIONAL_TESTING

    def setUp(self):
        self.mail_settings = get_portal_mail_settings()
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
        # self.mail_settings.email_from_address = u'portal@plone.test'
        self.mailhost = self.portal.MailHost
        # image for image testing
        self.folder.invokeFactory("Image", "image")
        self.image = self.folder.image
        image = self.folder['image']
        image.title = 'My Image'
        image.description = 'This is my image.'
        image.image = dummy_image(image)
        self.image = image

    def send_sample_message(self, body):
        self.assertSequenceEqual(self.mailhost.messages, [])
        self.newsletter.invokeFactory(
            "ENLIssue",
            id="issue")
        self.newsletter.issue.title = "with image"
        self.newsletter.issue.setText(body, mimetype='text/html')

        self.portal.REQUEST.form.update({
            'sender_name': self.newsletter.senderName,
            'sender_email': self.newsletter.senderEmail,
            'test_receiver': self.newsletter.testEmail,
            'subject': self.newsletter.issue.title,
            'test': 'submit',
        })
        self.portal.REQUEST['REQUEST_METHOD'] = 'POST'
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
        self.portal.REQUEST['REQUEST_METHOD'] = 'POST'
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

    def test_send_test_personalization(self):
        # with all infos
        api.content.create(
            type='ENLSubscriber',
            container=self.newsletter,
            salutation='ms',
            title='jane@example.com',
            firstname='Jane',
            lastname='Doe',
            email='jane@example.com'
        )
        # without salutation
        api.content.create(
            type='ENLSubscriber',
            container=self.newsletter,
            title='john@example.com',
            firstname='John',
            lastname='Doe',
            email='john@example.com'
        )
        # without firstname
        api.content.create(
            type='ENLSubscriber',
            container=self.newsletter,
            title='max@example.com',
            lastname='Mustermann',
            email='max@example.com'
        )
        # without lastname
        api.content.create(
            type='ENLSubscriber',
            container=self.newsletter,
            title='maxima@example.com',
            firstname='Maxima',
            email='maxima@example.com'
        )
        # without firstname and lastname
        api.content.create(
            type='ENLSubscriber',
            container=self.newsletter,
            title='leo@example.com',
            email='leo@example.com'
        )

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
        })
        self.portal.REQUEST['REQUEST_METHOD'] = 'POST'
        view = getMultiAdapter(
            (self.newsletter.issue, self.portal.REQUEST),
            name="send-issue")
        view = view.__of__(self.portal)
        view.send_issue()

        self.assertEqual(len(self.mailhost.messages), 5)
        self.assertTrue(self.mailhost.messages[0])
        self.assertTrue(self.mailhost.messages[1])

        msg1 = str(self.mailhost.messages[0])
        self.assertIn('To: <jane@example.com>', msg1)
        self.assertIn('Dear Ms. Jane Doe', msg1)

        msg2 = str(self.mailhost.messages[1])
        self.assertIn('To: <john@example.com>', msg2)
        self.assertIn('Dear John Doe', msg2)

        msg3 = str(self.mailhost.messages[2])
        self.assertIn('To: <max@example.com>', msg3)
        self.assertIn('Dear Mustermann', msg3)

        msg4 = str(self.mailhost.messages[3])
        self.assertIn('To: <maxima@example.com>', msg4)
        self.assertIn('Dear Maxima', msg4)

        msg5 = str(self.mailhost.messages[4])
        self.assertIn('To: <leo@example.com>', msg5)
        self.assertIn('Sir or Madam', msg5)

    def test_before_the_personalization_filter(self):
        def _personalize(event):
            edc = event.data['context']
            event.data['html'] = event.data['html'].replace('PHP', 'Python')
            firstname = edc['receiver'].get('firstname')
            lastname = edc['receiver'].get('lastname')
            if not firstname and not lastname:
                edc['SUBSCRIBER_SALUTATION'] = u'Dear {0}'.format(
                    edc['receiver']['email']
                )
        provideHandler(_personalize, [IBeforePersonalizationEvent])
        try:
            # with all infos
            api.content.create(
                type='ENLSubscriber',
                container=self.newsletter,
                salutation='ms',
                title='jane@example.com',
                firstname='Jane',
                lastname='Doe',
                email='jane@example.com'
            )
            # without firstname and lastname
            api.content.create(
                type='ENLSubscriber',
                container=self.newsletter,
                salutation='mr',
                title='john@example.com',
                email='john@example.com'
            )

            self.newsletter.invokeFactory(
                "ENLIssue",
                id="issue")
            self.newsletter.issue.title = \
                "This is a very long newsletter issue title with special "\
                "characters such as äüö. Will this really work?"
            self.newsletter.issue.setText(u'''
                <h1>PHP is cool</h1>
                {{SUBSCRIBER_SALUTATION}}
                ''')
            self.portal.REQUEST.form.update({
                'sender_name': self.newsletter.senderName,
                'sender_email': self.newsletter.senderEmail,
                'test_receiver': self.newsletter.testEmail,
                'subject': self.newsletter.issue.title,
            })
            self.portal.REQUEST['REQUEST_METHOD'] = 'POST'
            # clearEvents()  # noqa
            view = getMultiAdapter(
                (self.newsletter.issue, self.portal.REQUEST),
                name="send-issue")
            view = view.__of__(self.portal)
            view.send_issue()

            # pers_events = getEvents(IBeforePersonalizationFilter)
            # print(pers_events)
            self.assertEqual(len(self.mailhost.messages), 2)
            msg1 = str(self.mailhost.messages[0])
            self.assertIn('To: <jane@example.com>', msg1)
            self.assertIn('Dear Ms. Jane Doe', msg1)

            msg2 = str(self.mailhost.messages[1])
            self.assertIn('To: <john@example.com>', msg2)
            self.assertIn('Dear john@example.com', msg2)
        finally:
            getGlobalSiteManager().unregisterHandler(
                _personalize, [IBeforePersonalizationEvent])

    def test_send_test_issue_with_image(self):
        body = "<img src=\"{0}\"/>".format(
            self.image.absolute_url_path())
        msg = self.send_sample_message(body)

        self.assertIn('<img src=3D"cid:image_', msg)
        self.assertIn('Content-ID: <image_', msg)
        self.assertIn('Content-Type: image/png;', msg)

    def test_send_test_issue_with_scale_image(self):
        body = '<img src="{0}/@@images/image/thumb"/>'.format(
            self.image.absolute_url_path())

        # trigger scale generation:
        image_scales_url = '{0}/@@images'.format(
            self.image.absolute_url_path())
        scales = self.portal.restrictedTraverse(image_scales_url)
        scale_view = scales.scale(fieldname='image', scale='thumb')
        scale_view()
        # scale_view.index_html()
        zt.commit()

        msg = self.send_sample_message(body)
        self.assertIn('<img src=3D"cid:image_', msg)
        self.assertIn('Content-ID: <image_', msg)
        self.assertIn('Content-Type: image/png;', msg)

    def test_send_test_issue_with_resolveuid_image(self):
        if IS_PLONE_4:
            # for plone < 4.2 we need to ensure turn on to resolveuid links
            tinymce = queryUtility(ITinyMCE)
            if tinymce is None:
                return
            tinymce.link_using_uids = True

        body = '<img src="../../resolveuid/{0}"/>'.format(self.image.UID())

        msg = self.send_sample_message(body)

        self.assertNotIn('resolveuid', msg)
        self.assertIn('<img src=3D"cid:image_', msg)
        self.assertIn('Content-ID: <image_', msg)
        self.assertIn('Content-Type: image/png;', msg)

    # TODO: find a way to get the uid-based images in tests
    def test_send_test_issue_with_resolveuid_scale_image(self):
        if IS_PLONE_4:
            # for plone < 4.2 we need to ensure turn on to resolveuid links
            tinymce = queryUtility(ITinyMCE)
            if tinymce is None:
                return
            tinymce.link_using_uids = True

        path = "image/thumb"
        stack = path.split('/')
        body = '<img src="../../resolveuid/{0}/@@images/{1}"/>'.format(
            self.image.UID(), path)

        # trigger scale generation:
        image_scales_url = '{0}/@@images'.format(
            self.image.absolute_url_path())
        scales = self.portal.restrictedTraverse(image_scales_url)
        scale_view = scales.scale(fieldname=stack[0], scale=stack[1])
        scale_view()
        zt.commit()

        msg = self.send_sample_message(body)

        self.assertNotIn('resolveuid', msg)
        self.assertIn('<img src=3D"cid:image_', msg)
        self.assertIn('Content-ID: <image_', msg)
        self.assertIn('Content-Type: image/png;', msg)

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

        # Editor is not allowed to call the one-step send-issue meant for cron
        with self.assertRaises(Unauthorized):
            self.newsletter.restrictedTraverse("issue/send-issue")

        # check for postonly
        view = self.newsletter.restrictedTraverse("issue/send-issue-from-form")
        with self.assertRaises(Forbidden):
            view()


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
