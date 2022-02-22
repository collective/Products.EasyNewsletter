# -*- coding: utf-8 -*-

from datetime import datetime
from plone import api
from plone.namedfile.scaling import ImageScale, ImageScaling
from plone.protect import PostOnly
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _
from Products.EasyNewsletter.behaviors.plone_user_group_recipients import (
    IPloneUserGroupRecipients,
)
from Products.EasyNewsletter.content.newsletter_issue import ISendStatus
from Products.EasyNewsletter.interfaces import (
    IIssueDataFetcher,
    IReceiversPostSendingFilter,
)
from Products.Five.browser import BrowserView
from Products.MailHost.interfaces import IMailHost
from zope.component import getMultiAdapter, getUtility, subscribers
from zope.component.hooks import getSite

import emails
import emails.loader
import logging
import re
import transaction


log = logging.getLogger("Products.EasyNewsletter")


image_base_url = re.compile("(.*@@images)\/([a-zA-Z0-9.-]*)")


class ENLImageScale(ImageScale):
    """override validate_access method to allow access of privat objects"""

    def validate_access(self):
        return True


class ENLImageScaling(ImageScaling):
    _scale_view_class = ENLImageScale


class PloneMessageSendMixin:
    """ """


class Message(
    PloneMessageSendMixin,
    emails.message.MessageTransformerMixin,
    emails.message.MessageSignMixin,
    emails.message.MessageBuildMixin,
    emails.message.BaseMessage,
):
    """
    Email message with:
    - DKIM signer
    - mailhost compatible send
    - Message.transformer object
    """


class LocalLoader(object):
    """ """

    def __getitem__(self, uri):
        image_file = None
        portal = getSite()
        pstate = getMultiAdapter((portal, portal.REQUEST), name="plone_portal_state")
        purl = pstate.portal_url()
        url_match = image_base_url.match(uri)
        if url_match:
            groups = url_match.groups()
            print(groups)
            base_url = u""
            # url = "{0}/image/{1}".format(groups[0], groups[1])
            base_url = groups[0]
            image_scale = groups[1]
            scaling_view = portal.unrestrictedTraverse(
                base_url.replace(purl, "").lstrip("/")
            )
            scaled_image = scaling_view.scale("image", scale=image_scale)
            if not scaled_image:
                return
            image_file = scaled_image.data.open()
        else:
            # get the original image:
            image_obj = portal.unrestrictedTraverse(uri.replace(purl, "").lstrip("/"))
            if not image_obj:
                return
            if hasattr(image_obj, "image"):
                image_file = image_obj.image.open()
            elif hasattr(image_obj, "_data"):
                # OFS FSImage:
                image_file = image_obj._data
        return image_file

    def __contains__(self, uri):
        return self.__getitem__(uri)


class NewsletterIssueSend(BrowserView):
    @property
    def is_test(self):
        return self.request.form.get("test") or False

    def __call__(self):
        """
        sets workflow state to sending and then redirects to step2 with UID as
        parameter as simple safety belt.
        """
        PostOnly(self.request)
        if self.is_test:  # test must not modify the state
            self.send()
            api.portal.show_message(
                message=_("The issue test sending has been initiated."),
                request=self.request,
            )
            return self.request.response.redirect(self.context.absolute_url())

        # XXX implement this:
        # if self.context.issue_queue is not None:
        #     self._send_issue_prepare()
        #     self.context.queue_issue_for_sendout()
        #     api.portal.show_message(
        #         message=_("The issue sending has been initiated in the background."),
        #         request=self.request,
        #     )
        #     return self.request.response.redirect(self.context.absolute_url())

        # No queuing but direct send
        # self._send_issue_prepare()
        self.send_issue_immediately()
        api.portal.show_message(
            message=_("The issue has been generated and sent to the mail server."),
            request=self.request,
        )
        return self.request.response.redirect(self.context.absolute_url())

    def _send_issue_prepare(self):
        self.request["enlwf_guard"] = True
        api.content.transition(obj=self.context, transition="send")
        # commit the transaction so that identical incoming requests, for
        # whatever reason, will not trigger another send
        transaction.commit()
        self.request["enlwf_guard"] = False

    def send_issue_immediately(self):
        """convinience view for cron and similar

        never call this from UI - needs a way to protect
        currently manager only
        """
        self._send_issue_prepare()
        self.send()

    def send(self):
        """Sends the newsletter, sending might be queued for async send out."""

        # check for workflow
        current_state = api.content.get_state(obj=self.context)
        if not self.is_test and current_state != "sending":
            raise ValueError("Executed send in wrong review state!")

        # get hold of the parent Newsletter object#
        enl = self.context.get_newsletter()
        sender_name = self.request.get("sender_name") or enl.sender_name
        sender_email = self.request.get("sender_email") or enl.sender_email
        # get Plone email_charset
        # charset = get_email_charset()
        receivers = self._get_recipients()

        # determine MailHost first (build-in vs. external)
        delivery_service_name = "mailhost"  # XXX enl.delivery_dervice
        if delivery_service_name == "mailhost":
            self.mail_host = api.portal.get_tool("MailHost")
        else:
            self.mail_host = getUtility(IMailHost, name=delivery_service_name)
        log.info('Using mail delivery service "%r"' % self.mail_host)

        send_counter = 0
        send_error_counter = 0

        issue_data_fetcher = IIssueDataFetcher(self.context)
        # get issue subject an rendered output data
        issue_data = issue_data_fetcher()
        for receiver in receivers:
            personalized_html = issue_data_fetcher.personalize(
                receiver, issue_data["body_html"]
            )
            # get plain text version
            personalized_plaintext = issue_data_fetcher.create_plaintext_message(
                personalized_html
            )

            m = Message(
                html=personalized_html,
                text=personalized_plaintext,
                subject=issue_data["subject"],
                mail_from=(sender_name, sender_email),
                mail_to=(receiver["fullname"], receiver["email"]),
            )
            m.transformer.local_loader = LocalLoader()
            m.transform(
                images_inline=True,
                load_images=True,
                base_url=self.context.absolute_url(),
                cssutils_logging_level=logging.ERROR,
            )

            send_status = {
                "successful": None,
                "error": None,
                "datetime": datetime.now(),
            }

            msg_string = ""
            try:
                msg_string = m.as_string()
            except Exception as e:  # noqa
                send_status["successful"] = False
                send_status["error"] = e
                log.exception(
                    'Building newsletter email for "%s" failed, with error "%s"!'
                    % (receiver["email"], e)
                )
                send_error_counter += 1
                continue

            if "HTTPLoaderError" in msg_string:
                log.exception(u"Transform message failed: {0}".format(m.as_string()))

            try:
                self.mail_host.send(msg_string, immediate=True)
                send_status["successful"] = True
                log.info('Send newsletter to "%s"' % receiver["email"])
                send_counter += 1
            except Exception as e:  # noqa
                send_status["successful"] = False
                send_status["error"] = e
                log.exception(
                    'Sending newsletter to "%s" failed, with error "%s"!'
                    % (receiver["email"], e)
                )
                send_error_counter += 1
            finally:
                receiver["status"] = send_status
        # Add information to annotations
        status_adapter = ISendStatus(self.context)
        if status_adapter:
            status_adapter.add_records(receivers)
        log.info(
            "Newsletter was sent to (%s) receivers. (%s) errors occurred!"
            % (send_counter, send_error_counter)
        )

        # change status only for a 'regular' send operation (not 'is_test')
        if not self.is_test:
            self.request["enlwf_guard"] = True
            api.content.transition(obj=self.context, transition="sending_completed")
            self.request["enlwf_guard"] = False
            self.context.setEffectiveDate(datetime.now())
            self.context.reindexObject(idxs=["effective"])
            msg_type = "info"
            additional_warning = ""
            if send_error_counter:
                msg_type = "warn"
                additional_warning = _(
                    "\nPlease check the log files, for more details!"
                )
            api.portal.show_message(
                message=_(
                    "Newsletter was sent to ({0}) receivers. ({1}) errors occurred!{2}".format(
                        send_counter, send_error_counter, additional_warning
                    )
                ),
                request=self.request,
                type=msg_type,
            )

    @property
    def salutation_mappings(self):
        """
        returns mapping of salutations. Each salutation itself is a dict
        with key as language. (prepared for multilingual newsletter)
        """
        enl = self.context.get_newsletter()
        result = {}
        lang = self.context.language or "en"

        for line in enl.salutations:
            if "|" not in line:
                continue
            key, value = line.split("|")
            result[key.strip()] = {lang: value.strip()}
        return result

    def _unique_receivers(self, receivers_raw):
        receivers = []
        mails = []
        for receiver in receivers_raw:
            if receiver["email"] in mails:
                continue
            mails.append(receiver["email"])
            receivers.append(receiver)
        return receivers

    def _get_recipients(self):
        """return list of recipients"""
        request = self.request
        enl = self.context.get_newsletter()
        salutation_mappings = self.salutation_mappings
        if self.is_test:
            # get test e-mail
            test_receiver = request.get("test_receiver", "")
            if test_receiver == "":
                test_receiver = enl.test_email
            salutation = salutation_mappings.get("default", "")
            receivers = [
                {
                    "email": test_receiver,
                    "fullname": "Test Member",
                    "salutation": salutation.get(self.context.language, ""),
                    # 'nl_language': self.language
                }
            ]
            return receivers

        # only send to all subscribers if the exclude all subscribers
        # checkbox, was not set.
        # get Subscribers
        enl_receivers = []
        if not self.context.exclude_all_subscribers:
            for subscriber_brain in api.content.find(
                portal_type="Newsletter Subscriber", context=enl
            ):
                if not subscriber_brain:
                    continue
                subscriber = subscriber_brain.getObject()
                salutation_key = subscriber.salutation or "default"
                salutation = salutation_mappings.get(salutation_key, {})
                enl_receiver = {
                    "email": subscriber.email,
                    "gender": subscriber.salutation,
                    "name_prefix": subscriber.name_prefix,
                    "firstname": subscriber.firstname or u"",
                    "lastname": subscriber.lastname or u"",
                    "fullname": " ".join(
                        [subscriber.firstname or u"", subscriber.lastname or u""]
                    ),
                    "salutation": salutation.get(
                        None,  # subscriber.getNl_language(),
                        salutation.get(self.context.language or "en", ""),
                    ),
                    "uid": subscriber.UID(),
                    # 'nl_language': subscriber.getNl_language()
                }

                enl_receivers.append(enl_receiver)

        receivers_raw = enl_receivers

        # get subscribers over selected plone members anpid groups
        plone_receivers = []
        try:
            plone_receivers_adapter = IPloneUserGroupRecipients(self.context)
        except TypeError:
            plone_receivers_adapter = None
        if not plone_receivers_adapter:
            try:
                plone_receivers_adapter = IPloneUserGroupRecipients(enl)
            except TypeError:
                plone_receivers_adapter = None
        if plone_receivers_adapter:
            plone_receivers = plone_receivers_adapter.get_plone_subscribers()
        receivers_raw += plone_receivers
        # XXX implement this with the behavior
        # external_subscribers = self._get_external_source_subscribers(enl)
        # receivers_raw += external_subscribers
        receivers = self._unique_receivers(receivers_raw)

        # Run registered receivers post sending filters for INewsletter.
        for subscriber in subscribers([enl], IReceiversPostSendingFilter):
            receivers = subscriber.filter(receivers)

        # Run registered receivers post sending filters for INewsletterIssue.
        for subscriber in subscribers([self.context], IReceiversPostSendingFilter):
            receivers = subscriber.filter(receivers)

        return receivers
