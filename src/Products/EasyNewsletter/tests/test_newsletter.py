# -*- coding: utf-8 -*-

from App.Common import package_home
from plone import api
from plone.app.testing import login, setRoles, TEST_USER_ID, TEST_USER_NAME
from plone.app.textfield import RichTextValue
from Products.CMFPlone.tests.utils import MockMailHost
from Products.CMFPlone.utils import safe_unicode
from Products.EasyNewsletter.interfaces import IBeforePersonalizationEvent
from Products.EasyNewsletter.testing import PRODUCTS_EASYNEWSLETTER_FUNCTIONAL_TESTING
from Products.EasyNewsletter.tests.base import (
    parsed_attachments_from_msg,
    parsed_payloads_from_msg,
)
from Products.EasyNewsletter.utils.mail import get_portal_mail_settings
from Products.MailHost.interfaces import IMailHost
from zExceptions import Forbidden
from zope.component import (
    getGlobalSiteManager,
    getMultiAdapter,
    getSiteManager,
    provideHandler,
)

import os
import transaction as zt
import unittest


GLOBALS = globals()
TESTS_HOME = package_home(GLOBALS)


def dummy_image(imgname=u"img1.jpg"):
    from plone.namedfile.file import NamedBlobImage

    filename = os.path.join(os.path.dirname(__file__), imgname)
    with open(filename, "rb") as f:
        return NamedBlobImage(data=f.read(), filename=filename)


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
        )
        epilogue_output = self.newsletter.default_epilogue.output
        self.default_epilogue = RichTextValue(
            raw=epilogue_output,
            mimeType="text/html",
            outputMimeType="text/x-plone-outputfilters-html",
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
        # image1 for image testing
        self.folder.invokeFactory("Image", "image1")
        self.image1 = self.folder.image1
        image1 = self.folder["image1"]
        image1.title = "My Image 1"
        image1.description = "This is my image."
        image1.image = dummy_image()
        self.image1 = image1
        self.image1_tag = api.content.get_view("images", self.image1, self.request).tag(
            "image", "thumb"
        )

        # image2 for image testing
        self.folder.invokeFactory("Image", "image2")
        self.image2 = self.folder.image2
        image2 = self.folder["image2"]
        image2.title = "My Image 2"
        image2.description = "This is my image."
        image2.image = dummy_image(imgname=u"img2.jpg")
        self.image2 = image2
        image2_images = api.content.get_view("images", self.image2, self.request)
        self.image2_scale = image2_images.scale("image", "thumb")
        self.image2_url = self.image2_scale.url
        self.image2_uid = self.image2_scale.uid
        # image3 for image testing
        self.folder.invokeFactory("Image", "image3")
        self.image3 = self.folder.image3
        image3 = self.folder["image3"]
        image3.title = "My Image 3"
        image3.description = "This is my image."
        image3.image = dummy_image(imgname=u"img3.jpg")
        self.image3 = image3
        image3_images = api.content.get_view("images", self.image3, self.request)
        self.image3_scale = image3_images.scale("image", "thumb")
        self.image3_url = self.image3_scale.url
        self.image3_uid = self.image3_scale.uid

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
        return safe_unicode(self.mailhost.messages[0])

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
        msg = safe_unicode(self.mailhost.messages[0])
        parsed_payloads = parsed_payloads_from_msg(msg)
        self.assertIn(u"Test Member", parsed_payloads["to"])
        self.assertIn(u"<test@acme.com>", parsed_payloads["to"])
        self.assertIn(u"<newsletter@acme.com>", parsed_payloads["from"])
        self.assertIn(u"ACME newsletter", parsed_payloads["from"])

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

        msg1 = safe_unicode(self.mailhost.messages[0])
        parsed_payloads1 = parsed_payloads_from_msg(msg1)
        self.assertIn(u"Jane Doe", parsed_payloads1["to"])
        self.assertIn(u"<jane@example.com>", parsed_payloads1["to"])
        self.assertIn(u"Dear Ms. Jane Doe", safe_unicode(parsed_payloads1["text/html"]))

        msg2 = safe_unicode(self.mailhost.messages[1])
        parsed_payloads2 = parsed_payloads_from_msg(msg2)
        self.assertIn(u"John Doe", parsed_payloads2["to"])
        self.assertIn(u"Dear John Doe", safe_unicode(parsed_payloads2["text/html"]))

        msg3 = safe_unicode(self.mailhost.messages[2])
        parsed_payloads3 = parsed_payloads_from_msg(msg3)
        self.assertIn(u"Mustermann", parsed_payloads3["to"])
        self.assertIn(u"<max@example.com>", parsed_payloads3["to"])
        self.assertIn(u"Dear Mustermann", safe_unicode(parsed_payloads3["text/html"]))

        msg4 = safe_unicode(self.mailhost.messages[3])
        parsed_payloads4 = parsed_payloads_from_msg(msg4)
        self.assertIn(u"Maxima", parsed_payloads4["to"])
        self.assertIn(u"<maxima@example.com>", parsed_payloads4["to"])
        self.assertIn(u"Dear Maxima", safe_unicode(parsed_payloads4["text/html"]))

        msg5 = safe_unicode(self.mailhost.messages[4])
        parsed_payloads5 = parsed_payloads_from_msg(msg5)
        self.assertIn(u"leo@example.com", parsed_payloads5["to"])
        self.assertIn(u"Sir or Madam", safe_unicode(parsed_payloads5["text/html"]))

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
            msg1 = safe_unicode(self.mailhost.messages[0])
            parsed_payloads1 = parsed_payloads_from_msg(msg1)
            self.assertIn(u"Jane Doe", parsed_payloads1["to"])
            self.assertIn(u"<jane@example.com>", parsed_payloads1["to"])
            self.assertIn(
                u"Dear Ms. Jane Doe", safe_unicode(parsed_payloads1["text/html"])
            )

            msg2 = safe_unicode(self.mailhost.messages[1])
            parsed_payloads2 = parsed_payloads_from_msg(msg2)
            self.assertIn(u"john@example.com", parsed_payloads2["to"])
            self.assertIn(
                u"Dear john@example.com", safe_unicode(parsed_payloads2["text/html"])
            )
        finally:
            getGlobalSiteManager().unregisterHandler(
                _personalize, [IBeforePersonalizationEvent]
            )

    def test_send_test_issue_with_image(self):
        body = u'<img src="{0}"/>'.format(self.image1.absolute_url_path())
        msg = self.send_sample_message(body)
        parsed_payloads = parsed_payloads_from_msg(msg)
        self.assertIn(u'src="cid:image', safe_unicode(parsed_payloads["text/html"]))
        self.assertIn(u"Content-ID: <image", safe_unicode(msg))
        self.assertIn(u"Content-Type: image/jpeg;", safe_unicode(msg))

    def test_send_test_issue_with_scale_image(self):
        body = '<img src="{0}/@@images/image/thumb"/>'.format(
            self.image1.absolute_url_path()
        )

        # trigger scale generation:
        image_scales_url = "{0}/@@images".format(self.image1.absolute_url_path())
        scales = self.portal.restrictedTraverse(image_scales_url)
        scale_view = scales.scale(fieldname="image", scale="thumb")
        scale_view()
        # scale_view.index_html()
        zt.commit()

        msg = self.send_sample_message(body)
        parsed_payloads = parsed_payloads_from_msg(msg)
        self.assertIn(u'src="cid:thumb', safe_unicode(parsed_payloads["text/html"]))
        self.assertIn(u"Content-ID: <thumb", safe_unicode(msg))
        self.assertIn(u"Content-Type: image/jpeg;", safe_unicode(msg))

    def test_send_test_issue_with_resolveuid_image(self):
        body = '<img src="../../resolveuid/{0}"/>'.format(self.image1.UID())

        msg = self.send_sample_message(body)
        parsed_payloads = parsed_payloads_from_msg(msg)
        self.assertNotIn("resolveuid", safe_unicode(parsed_payloads["text/html"]))
        self.assertIn(u'src="cid:image', safe_unicode(parsed_payloads["text/html"]))
        self.assertIn(u"Content-ID: <image", msg)
        self.assertIn(u"Content-Type: image/jpeg;", msg)

    def test_send_test_issue_with_resolveuid_scale_image(self):
        path = "image/thumb"
        stack = path.split("/")

        # trigger scale generation:
        image_scales_url = "{0}/@@images".format(self.image1.absolute_url_path())
        scales = self.portal.restrictedTraverse(image_scales_url)
        scale_view = scales.scale(fieldname=stack[0], scale=stack[1])
        image_scale = scale_view()
        body = u'<img src="{0}"/>'.format(image_scale.absolute_url())
        zt.commit()
        msg = self.send_sample_message(body)
        parsed_payloads = parsed_payloads_from_msg(msg)
        self.assertNotIn(u"resolveuid", safe_unicode(parsed_payloads["text/html"]))
        self.assertIn(
            u'src="cid:{0}"'.format(image_scale.__name__),
            safe_unicode(parsed_payloads["text/html"]),
        )
        self.assertIn(u"Content-ID: <{0}>".format(image_scale.__name__), msg)
        self.assertIn(u"Content-Type: image/jpeg;", msg)

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
            u"mailonly" not in safe_unicode(view_result),
            "get-public-body view contains mailonly elements,"
            " this should filtert out!",
        )

    def test_send_test_issue_with_multiple_images(self):
        body = u"""<h1>Headline</h1><br />
        {0}
        <img src="{1}" />
        <img src="{2}" />
        """.format(
            self.image1_tag, self.image2_url, self.image3_url,
        )
        msg = self.send_sample_message(body)
        print(msg)
        parsed_payloads = parsed_payloads_from_msg(msg)
        self.assertIn(
            u'src="cid:{0}'.format(self.image3_uid),
            safe_unicode(parsed_payloads["text/html"]),
        )
        self.assertIn(
            u"Content-ID: <{0}.jpeg>".format(self.image2_uid), safe_unicode(msg)
        )
        self.assertIn(
            u"Content-ID: <{0}.jpeg>".format(self.image3_uid), safe_unicode(msg)
        )
        self.assertIn(u"Content-Type: image/jpeg;", safe_unicode(msg))

        attachments = parsed_attachments_from_msg(msg)
        self.assertIn(u"{0}.jpeg".format(self.image2_uid), attachments)
        self.assertIn(u"{0}.jpeg".format(self.image3_uid), attachments)
        print(attachments)

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
