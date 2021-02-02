# -*- coding: utf-8 -*-

from plone import api
from Products.EasyNewsletter import _
from Products.EasyNewsletter.utils.mail import get_portal_mail_settings
from Products.Five.browser import BrowserView
from zope.i18n import translate


# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class NewsletterUnsubscribeForm(BrowserView):
    def __call__(self):
        self.newsletter_url = self.context.absolute_url()
        subscriber = self.request.get("subscriber")

        if subscriber:
            self.send_unsubscribe_email(subscriber)
            return self.request.response.redirect(self.newsletter_url)
        else:
            self.form_action = self.newsletter_url + "/unsubscribe"
            return self.index()

    def send_unsubscribe_email(self, subscriber):
        newsletter = self.context
        catalog = api.portal.get_tool(name="portal_catalog")
        query = {}
        query["portal_type"] = "Newsletter Subscriber"
        query["email"] = subscriber
        results = catalog.unrestrictedSearchResults(query)
        if results:
            subscriber_brain = results[0]
            unsubscribe_url = (
                self.newsletter_url + "/unsubscribe?subscriber=" + subscriber_brain.UID
            )
            unsubscribe_header_msgid = _(
                u"you_requested_to_unsubscribe",
                default=u"You requested to unsubscribe from the following newsletter: ${title}",
                mapping={u"title": newsletter.title},
            )
            msg_text = "{0}\n{1}: {2}".format(
                translate(unsubscribe_header_msgid),
                newsletter.unsubscribe_string,
                unsubscribe_url,
            )
            settings = get_portal_mail_settings()
            api.portal.send_email(
                recipient=subscriber,
                sender=settings.email_from_address,
                subject=u"{0}: {1}".format(
                    newsletter.title, _(u"confirm newsletter unsubscription")
                ),
                body=msg_text,
            )
            api.portal.show_message(
                message=_("We send you an email, please confirm this unsubscription."),
                request=self.request,
                type="info",
            )
        else:
            # todo: write an extra error msg if a plone user wants to
            # unsubscribe himself
            api.portal.show_message(
                message=_("Your email address could not be found in subscribers."),
                request=self.request,
                type="error",
            )
