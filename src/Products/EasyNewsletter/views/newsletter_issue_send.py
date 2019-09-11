# -*- coding: utf-8 -*-
from plone import api
from plone.protect import PostOnly
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _  # noqa
from Products.EasyNewsletter.interfaces import IIssueDataFetcher
from Products.EasyNewsletter.utils.mail import get_email_charset
from Products.Five.browser import BrowserView
from Products.MailHost.interfaces import IMailHost
from zope.component import getUtility

import emails
import logging
import transaction


log = logging.getLogger('Products.EasyNewsletter')


class PloneMessageSendMixin():
    """
    """
    def __init__(self):
        pass


class Message(PloneMessageSendMixin, emails.message.MessageTransformerMixin, emails.message.MessageSignMixin, emails.message.MessageBuildMixin, emails.message.BaseMessage):
    """
    Email message with:
    - DKIM signer
    - mailhost compatible send
    - Message.transformer object
    """


class NewsletterIssueSend(BrowserView):
    @property
    def is_test(self):
        return self.request.form.get('test') or False

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
        self._send_issue_prepare()
        self.send_issue_immediately()
        api.portal.show_message(
            message=_("The issue has been generated and sent to the mail server."),
            request=self.request,
        )
        return self.request.response.redirect(self.context.absolute_url())

    def _send_issue_prepare(self):
        self.request['enlwf_guard'] = True
        api.content.transition(obj=self.context, transition='send')
        # commit the transaction so that identical incoming requests, for
        # whatever reason, will not trigger another send
        transaction.commit()
        self.request['enlwf_guard'] = False

    def send_issue_immediately(self):
        """convinience view for cron and similar

        never call this from UI - needs a way to protect
        currently manager only
        """
        self.send()

    def send(self):
        """Sends the newsletter, sending might be queued for async send out.
        """

        # check for workflow
        current_state = api.content.get_state(obj=self.context)
        if not self.is_test and current_state != 'sending':
            raise ValueError('Executed send in wrong review state!')

        # get hold of the parent Newsletter object#
        enl = self.context.get_newsletter()
        sender_name = self.request.get('sender_name') or enl.sender_name
        sender_email = self.request.get('sender_email') or enl.sender_email
        # get Plone email_charset
        # charset = get_email_charset()
        receivers = self._get_recipients()

        # determine MailHost first (build-in vs. external)
        delivery_service_name = 'mailhost'  # XXX enl.delivery_dervice
        if delivery_service_name == 'mailhost':
            self.mail_host = api.portal.get_tool('MailHost')
        else:
            self.mail_host = getUtility(IMailHost, name=delivery_service_name)
        log.info('Using mail delivery service "%r"' % self.mail_host)

        send_counter = 0
        send_error_counter = 0

        issue_data_fetcher = IIssueDataFetcher(self.context)
        # get issue data
        issue_data = issue_data_fetcher()
        for receiver in receivers:
            personalized_html = issue_data_fetcher.personalize(receiver, issue_data['body_html'])
            # get plain text version
            personalized_plaintext = issue_data_fetcher.create_plaintext_message(
                personalized_html
            )

            m = emails.Message(
                html=personalized_html,
                text=personalized_plaintext,
                subject=issue_data['subject'],
                mail_from=(sender_name, sender_email),
                mail_to=(receiver['fullname'], receiver['email']),
            )
            # # create multipart mail
            # outer = MIMEMultipart('alternative')
            # outer['To'] = Header(u'<%s>' % safe_unicode(receiver['email']))
            # outer['From'] = from_header
            # outer['Subject'] = issue_data['subject_header']
            # outer.epilogue = ''

            # # Attach text part
            # text_part = MIMEText(issue_data['body_plain'], 'plain', charset)

            # # Attach html part with images
            # html_part = MIMEMultipart('related')
            # html_text = MIMEText(issue_data['body_html'], 'html', charset)
            # html_part.attach(html_text)
            # # Add images to the message
            # for image in issue_data['images_to_attach']:
            #     html_part.attach(image)
            # outer.attach(text_part)
            # outer.attach(html_part)

            try:
                self.mail_host.send(m.as_string())
                log.info('Send newsletter to "%s"' % receiver['email'])
                send_counter += 1
            except Exception, e:  # noqa
                log.exception(
                    'Sending newsletter to "%s" failed, with error "%s"!'
                    % (receiver['email'], e))
                send_error_counter += 1

        log.info(
            'Newsletter was sent to (%s) receivers. (%s) errors occurred!'
            % (send_counter, send_error_counter))

        # change status only for a 'regular' send operation (not 'is_test')
        if not self.is_test:
            self.request['enlwf_guard'] = True
            api.content.transition(obj=self, transition='sending_completed')
            self.request['enlwf_guard'] = False
            self.setEffectiveDate(DateTime())
            self.reindexObject(idxs=['effective'])

    @property
    def salutation_mappings(self):
        """
        returns mapping of salutations. Each salutation itself is a dict
        with key as language. (prepared for multilingual newsletter)
        """
        enl = self.context.get_newsletter()
        result = {}
        lang = self.context.language or 'en'

        for line in enl.salutations:
            if "|" not in line:
                continue
            key, value = line.split('|')
            result[key.strip()] = {lang: value.strip()}
        return result

    def _get_recipients(self):
        """ return list of recipients """
        request = self.request
        enl = self.context.get_newsletter()
        salutation_mappings = self.salutation_mappings
        if self.is_test:
            # get test e-mail
            test_receiver = request.get('test_receiver', '')
            if test_receiver == "":
                test_receiver = enl.test_email
            salutation = salutation_mappings.get('default', '')
            receivers = [{
                'email': test_receiver,
                'fullname': 'Test Member',
                'salutation': salutation.get(self.context.language, ''),
                # 'nl_language': self.language
            }]
            return receivers

        # only send to all subscribers if the exclude all subscribers
        # checkbox, was not set.
        # get ENLSubscribers
        enl_receivers = []
        if not self.exclude_all_subscribers:
            for subscriber in enl.objectValues('ENLSubscriber'):
                salutation_key = subscriber.getSalutation() or 'default'
                salutation = salutation_mappings.get(salutation_key, {})
                enl_receiver = {
                    'email': subscriber.getEmail(),
                    'gender': subscriber.getSalutation(),
                    'name_prefix': subscriber.getName_prefix(),
                    'firstname': subscriber.getFirstname(),
                    'lastname': subscriber.getLastname(),
                    'fullname': ' '.join([subscriber.getFirstname(),
                                          subscriber.getLastname()]),
                    'salutation': salutation.get(
                        # subscriber.getNl_language(),
                        salutation.get(self.language or 'en', '')
                    ),
                    'uid': subscriber.UID(),
                    # 'nl_language': subscriber.getNl_language()
                }

                enl_receivers.append(enl_receiver)

        # get subscribers over selected plone members and groups
        plone_receivers = self.get_plone_subscribers()
        external_subscribers = self._get_external_source_subscribers(enl)
        receivers_raw = plone_receivers + enl_receivers + \
            external_subscribers
        receivers = self._unique_receivers(receivers_raw)

        return receivers
