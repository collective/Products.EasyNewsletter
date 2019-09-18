# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from App.Common import package_home
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.textfield import RichTextValue
from Products.CMFPlone.tests.utils import MockMailHost
from Products.EasyNewsletter.config import IS_PLONE_5
from Products.EasyNewsletter.content.newsletter import INewsletter
from Products.EasyNewsletter.content.newsletter_issue import INewsletterIssue
from Products.EasyNewsletter.interfaces import IBeforePersonalizationEvent
from Products.EasyNewsletter.testing import PRODUCTS_EASYNEWSLETTER_FUNCTIONAL_TESTING
from Products.EasyNewsletter.tests.base import parsed_payloads_from_msg
from Products.EasyNewsletter.utils.mail import get_portal_mail_settings
from Products.MailHost.interfaces import IMailHost
from zExceptions import Forbidden
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.component import getSiteManager
from zope.component import provideHandler
from zope.component import queryUtility
from zope.interface import Interface

import base64
import email
import os
import pkg_resources
import six
import transaction as zt
import unittest


try:
    pkg_resources.get_distribution("Products.TinyMCE")
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
    filename = os.path.join(os.path.dirname(__file__), u"img1.png")
    if not IS_PLONE_5:  # BBB
        image.edit(image=open(filename, "r").read())
    else:
        return NamedBlobImage(data=open(filename, "r").read(), filename=filename)


class EasyNewsletterTests(unittest.TestCase):
    # layer = PRODUCTS_EASYNEWSLETTER_FUNCTIONAL_TESTING
    layer = PRODUCTS_EASYNEWSLETTER_FUNCTIONAL_TESTING

    def setUp(self):
        self.mail_settings = get_portal_mail_settings()
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory("Folder", "test-folder")
        self.folder = self.portal["test-folder"]
        self.portal = self.layer["portal"]
        self.folder.invokeFactory("Newsletter", "newsletter")
        self.newsletter = self.folder.newsletter
        self.newsletter.sender_email = "newsletter@acme.com"
        self.newsletter.sender_name = "ACME newsletter"
        self.newsletter.test_email = "test@acme.com"
        prologue_output = self.newsletter.default_prologue.output
        self.default_prologue = RichTextValue(
            raw=prologue_output,
            mimeType="text/html",
            outputMimeType="text/x-plone-outputfilters-html",
            encoding="utf-8",
        )
        epilogue_output = self.newsletter.default_epilogue.output
        self.default_epilogue = RichTextValue(
            raw=epilogue_output,
            mimeType="text/html",
            outputMimeType="text/x-plone-outputfilters-html",
            encoding="utf-8",
        )

        # Set up a mock mailhost
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost("MailHost")
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)
        # We need to fake a valid mail setup
        # self.mail_settings.email_from_address = u'portal@plone.test'
        self.mailhost = self.portal.MailHost
        # image for image testing
        self.folder.invokeFactory("Image", "image")
        self.image = self.folder.image
        image = self.folder["image"]
        image.title = "My Image"
        image.description = "This is my image."
        image.image = dummy_image(image)
        self.image = image

    def send_sample_message(self, body):
        self.assertSequenceEqual(self.mailhost.messages, [])
        self.issue = api.content.create(
            type="Newsletter Issue",
            id="issue",
            title=u"with image",
            container=self.newsletter,
        )
        self.issue.text = RichTextValue(
            raw=body,
            mimeType="text/html",
            outputMimeType="text/x-plone-outputfilters-html",
            encoding="utf-8",
        )
        self.issue.prologue = self.default_prologue
        self.issue.epilogue = self.default_epilogue
        self.issue.output_template = "output_default"

        self.portal.REQUEST.form.update(
            {
                "sender_name": self.newsletter.sender_name,
                "sender_email": self.newsletter.sender_email,
                "test_receiver": self.newsletter.test_email,
                "subject": self.issue.title,
                "test": "submit",
            }
        )
        self.portal.REQUEST["REQUEST_METHOD"] = "POST"
        zt.commit()
        view = getMultiAdapter((self.issue, self.portal.REQUEST), name="send-issue")

        view()

        self.assertEqual(len(self.mailhost.messages), 1)
        self.assertTrue(self.mailhost.messages[0])
        return str(self.mailhost.messages[0])

    def test_create_newsletter(self):
        self.assertTrue(INewsletter.providedBy(self.newsletter))

    def test_create_issue(self):
        self.issue = api.content.create(
            type="Newsletter Issue",
            id="issue",
            title=u"Issue 1",
            container=self.newsletter,
        )
        self.assertTrue(INewsletterIssue.providedBy(self.issue))

    def test_issue_send_test(self):
        self.issue = api.content.create(
            type="Newsletter Issue",
            id="issue",
            title=u"Issue 1",
            container=self.newsletter,
        )
        self.issue.title = (
            "This is a very long newsletter issue title with special "
            "characters such as äüö. Will this really work?"
        )
        # self.issue.text = RichTextValue(
        #     raw=u'nothing',
        #     mimeType="text/html",
        #     outputMimeType="text/x-plone-outputfilters-html",
        #     encoding="utf-8",
        # )
        self.issue.output_template = "output_default"
        zt.commit()

        self.portal.REQUEST.form.update(
            {
                "sender_name": self.newsletter.sender_name,
                "sender_email": self.newsletter.sender_email,
                "test_receiver": self.newsletter.test_email,
                "subject": self.issue.title,
                "test": "submit",
            }
        )
        self.portal.REQUEST["REQUEST_METHOD"] = "POST"
        view = getMultiAdapter((self.issue, self.portal.REQUEST), name="send-issue")

        view()
        self.assertEqual(len(self.mailhost.messages), 1)
        self.assertTrue(self.mailhost.messages[0])
        msg = str(self.mailhost.messages[0])
        parsed_payloads = parsed_payloads_from_msg(msg)
        self.assertIn("To: Test Member <test@acme.com>", msg)
        self.assertIn("From: ACME newsletter <newsletter@acme.com>", msg)

    def test_send_test_personalization(self):
        # with all infos
        api.content.create(
            type="Newsletter Subscriber",
            container=self.newsletter,
            salutation="ms",
            title="jane@example.com",
            firstname="Jane",
            lastname="Doe",
            email="jane@example.com",
        )
        # without salutation
        api.content.create(
            type="Newsletter Subscriber",
            container=self.newsletter,
            title="john@example.com",
            firstname="John",
            lastname="Doe",
            email="john@example.com",
        )
        # without firstname
        api.content.create(
            type="Newsletter Subscriber",
            container=self.newsletter,
            title="max@example.com",
            lastname="Mustermann",
            email="max@example.com",
        )
        # without lastname
        api.content.create(
            type="Newsletter Subscriber",
            container=self.newsletter,
            title="maxima@example.com",
            firstname="Maxima",
            email="maxima@example.com",
        )
        # without firstname and lastname
        api.content.create(
            type="Newsletter Subscriber",
            container=self.newsletter,
            title="leo@example.com",
            email="leo@example.com",
        )
        body = u"Some body content, in the issue."
        self.issue = api.content.create(
            type="Newsletter Issue",
            id="issue",
            title=(
                "This is a very long newsletter issue title with special "
                "characters such as äüö. Will this really work?"
            ),
            container=self.newsletter,
            prologue=self.default_prologue,
            epilogue=self.default_epilogue,
            text=RichTextValue(
                raw=body,
                mimeType="text/html",
                outputMimeType="text/x-plone-outputfilters-html",
                encoding="utf-8",
            ),
            output_template="output_default",
        )
        zt.commit()
        self.portal.REQUEST.form.update(
            {
                "sender_name": self.newsletter.sender_name,
                "sender_email": self.newsletter.sender_email,
                "test_receiver": self.newsletter.test_email,
                "subject": self.issue.title,
            }
        )
        self.portal.REQUEST["REQUEST_METHOD"] = "POST"
        view = getMultiAdapter((self.issue, self.portal.REQUEST), name="send-issue")
        view()

        self.assertEqual(len(self.mailhost.messages), 5)
        self.assertTrue(self.mailhost.messages[0])
        self.assertTrue(self.mailhost.messages[1])

        msg1 = str(self.mailhost.messages[0])
        parsed_payloads1 = parsed_payloads_from_msg(msg1)
        self.assertIn("To: Jane Doe <jane@example.com>", msg1)
        self.assertIn("Dear Ms. Jane Doe", parsed_payloads1["text/html"])

        msg2 = str(self.mailhost.messages[1])
        parsed_payloads2 = parsed_payloads_from_msg(msg2)
        self.assertIn("To: John Doe <john@example.com>", msg2)
        self.assertIn("Dear John Doe", parsed_payloads2["text/html"])

        msg3 = str(self.mailhost.messages[2])
        parsed_payloads3 = parsed_payloads_from_msg(msg3)
        self.assertIn("To: Mustermann <max@example.com>", msg3)
        self.assertIn("Dear Mustermann", parsed_payloads3["text/html"])

        msg4 = str(self.mailhost.messages[3])
        parsed_payloads4 = parsed_payloads_from_msg(msg4)
        self.assertIn("To: Maxima <maxima@example.com>", msg4)
        self.assertIn("Dear Maxima", parsed_payloads4["text/html"])

        msg5 = str(self.mailhost.messages[4])
        parsed_payloads5 = parsed_payloads_from_msg(msg5)
        self.assertIn("To: leo@example.com", msg5)
        self.assertIn("Sir or Madam", parsed_payloads5["text/html"])

    def test_before_the_personalization_filter(self):
        def _personalize(event):
            edc = event.data["context"]
            event.data["html"] = event.data["html"].replace("PHP", "Python")
            firstname = edc["receiver"].get("firstname")
            lastname = edc["receiver"].get("lastname")
            if not firstname and not lastname:
                edc["SUBSCRIBER_SALUTATION"] = u"Dear {0}".format(
                    edc["receiver"]["email"]
                )

        provideHandler(_personalize, [IBeforePersonalizationEvent])
        try:
            # with all infos
            api.content.create(
                type="Newsletter Subscriber",
                container=self.newsletter,
                salutation="ms",
                title="jane@example.com",
                firstname="Jane",
                lastname="Doe",
                email="jane@example.com",
            )
            # without firstname and lastname
            api.content.create(
                type="Newsletter Subscriber",
                container=self.newsletter,
                salutation="mr",
                title="john@example.com",
                email="john@example.com",
            )

            self.issue = api.content.create(
                type="Newsletter Issue",
                id="issue",
                title=u"Issue 1",
                container=self.newsletter,
            )
            self.issue.title = (
                "This is a very long newsletter issue title with special "
                "characters such as äüö. Will this really work?"
            )
            body = u"""
                <h1>PHP is cool</h1>
                {{SUBSCRIBER_SALUTATION}}
                """
            self.issue.text = RichTextValue(
                raw=body,
                mimeType="text/html",
                outputMimeType="text/x-plone-outputfilters-html",
                encoding="utf-8",
            )
            self.issue.prologue = self.default_prologue
            self.issue.epilogue = self.default_epilogue
            self.issue.output_template = "output_default"
            self.portal.REQUEST.form.update(
                {
                    "sender_name": self.newsletter.sender_name,
                    "sender_email": self.newsletter.sender_email,
                    "test_receiver": self.newsletter.test_email,
                    "subject": self.issue.title,
                }
            )
            self.portal.REQUEST["REQUEST_METHOD"] = "POST"
            zt.commit()
            # clearEvents()  # noqa
            view = getMultiAdapter((self.issue, self.portal.REQUEST), name="send-issue")
            view()

            # pers_events = getEvents(IBeforePersonalizationFilter)
            # print(pers_events)
            self.assertEqual(len(self.mailhost.messages), 2)
            msg1 = str(self.mailhost.messages[0])
            parsed_payloads1 = parsed_payloads_from_msg(msg1)
            self.assertIn("To: Jane Doe <jane@example.com>", msg1)
            self.assertIn("Dear Ms. Jane Doe", parsed_payloads1["text/html"])

            msg2 = str(self.mailhost.messages[1])
            parsed_payloads2 = parsed_payloads_from_msg(msg2)
            self.assertIn("To: john@example.com", msg2)
            self.assertIn("Dear john@example.com", parsed_payloads2["text/html"])
        finally:
            getGlobalSiteManager().unregisterHandler(
                _personalize, [IBeforePersonalizationEvent]
            )

    def test_send_test_issue_with_image(self):
        body = '<img src="{0}"/>'.format(self.image.absolute_url_path())
        msg = self.send_sample_message(body)
        parsed_payloads = parsed_payloads_from_msg(msg)

        self.assertIn('src="cid:image', parsed_payloads["text/html"])
        self.assertIn("Content-ID: <image", msg)
        self.assertIn("Content-Type: image/png;", msg)

    def test_send_test_issue_with_scale_image(self):
        body = '<img src="{0}/@@images/image/thumb"/>'.format(
            self.image.absolute_url_path()
        )

        # trigger scale generation:
        image_scales_url = "{0}/@@images".format(self.image.absolute_url_path())
        scales = self.portal.restrictedTraverse(image_scales_url)
        scale_view = scales.scale(fieldname="image", scale="thumb")
        scale_view()
        # scale_view.index_html()
        zt.commit()

        msg = self.send_sample_message(body)
        parsed_payloads = parsed_payloads_from_msg(msg)
        self.assertIn('src="cid:thumb', parsed_payloads["text/html"])
        self.assertIn("Content-ID: <thumb", msg)
        self.assertIn("Content-Type: image/png;", msg)

    def test_send_test_issue_with_resolveuid_image(self):
        body = '<img src="../../resolveuid/{0}"/>'.format(self.image.UID())

        msg = self.send_sample_message(body)
        parsed_payloads = parsed_payloads_from_msg(msg)
        self.assertNotIn("resolveuid", parsed_payloads["text/html"])
        self.assertIn('src="cid:image', parsed_payloads["text/html"])
        self.assertIn("Content-ID: <image", msg)
        self.assertIn("Content-Type: image/png;", msg)

    def test_send_test_issue_with_resolveuid_scale_image(self):
        path = "image/thumb"
        stack = path.split("/")

        # trigger scale generation:
        image_scales_url = "{0}/@@images".format(self.image.absolute_url_path())
        scales = self.portal.restrictedTraverse(image_scales_url)
        scale_view = scales.scale(fieldname=stack[0], scale=stack[1])
        image_scale = scale_view()
        body = '<img src="{0}"/>'.format(image_scale.absolute_url())
        zt.commit()
        msg = self.send_sample_message(body)
        parsed_payloads = parsed_payloads_from_msg(msg)
        self.assertNotIn("resolveuid", parsed_payloads["text/html"])
        self.assertIn('src="cid:{0}"'.format(image_scale.__name__),  parsed_payloads["text/html"])
        self.assertIn("Content-ID: <{0}>".format(image_scale.__name__), msg)
        self.assertIn("Content-Type: image/png;", msg)

    def test_mailonly_filter_in_issue_public_view(self):
        self.issue = api.content.create(
            type="Newsletter Issue",
            id="issue",
            title=u"Issue 1",
            container=self.newsletter,
        )
        self.issue.title = "Test Newsletter Issue"
        body = (
            '<h1>This is the newsletter body!</h1><div class="mailonly">'
            "This test should only visible in mails not in public view!</div>"
        )
        self.issue.text = RichTextValue(
            raw=body,
            mimeType="text/html",
            outputMimeType="text/x-plone-outputfilters-html",
            encoding="utf-8",
        )
        self.issue.prologue = self.default_prologue
        self.issue.epilogue = self.default_epilogue
        self.issue.output_template = "output_default"
        zt.commit()
        view = getMultiAdapter(
            (self.issue, self.portal.REQUEST), name="get-public-body"
        )
        view_result = view()

        self.assertTrue(
            "mailonly" not in view_result,
            "get-public-body view contains mailonly elements,"
            " this should filtert out!",
        )

    def test_permission(self):
        setRoles(self.portal, TEST_USER_ID, ["Editor"])
        self.portal.REQUEST.set("ACTUAL_URL", "http://nohost")
        self.issue = api.content.create(
            type="Newsletter Issue",
            id="issue",
            title=u"Issue 1",
            container=self.newsletter,
        )
        self.issue.title = "Test Newsletter Issue"
        body = "<h1>This is the newsletter body!"
        self.issue.text = RichTextValue(
            raw=body,
            mimeType="text/html",
            outputMimeType="text/x-plone-outputfilters-html",
            encoding="utf-8",
        )
        self.issue.prologue = self.default_prologue
        self.issue.epilogue = self.default_epilogue
        self.issue.output_template = "output_default"

        view = getMultiAdapter(
            (self.newsletter, self.portal.REQUEST), name="newsletter-drafts"
        )
        view_result = view()
        self.assertIn("test-folder/newsletter/issue", view_result)

        view = self.newsletter.restrictedTraverse("issue/send-issue-form")
        view_result = view()

        self.assertIn("Test Newsletter", view_result)

        # Editor is not allowed to call the one-step send-issue meant for cron
        # XXX
        # with self.assertRaises(Unauthorized):
        #     self.newsletter.restrictedTraverse("issue/send-issue-immediately")

        # check for postonly
        view = self.newsletter.restrictedTraverse("issue/send-issue")
        with self.assertRaises(Forbidden):
            view()


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
