# -*- coding: utf-8 -*-

from AccessControl.SecurityManagement import newSecurityManager
from plone import api
from plone import protect
from Products.EasyNewsletter import _
from Products.EasyNewsletter.content.newsletter import INewsletter
from Products.EasyNewsletter.content.newsletter_subscriber import INewsletterSubscriber
from Products.EasyNewsletter.utils.mail import get_portal_mail_settings
from Products.Five.browser import BrowserView
from zope.interface import alsoProvides


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
            msg_text = """%s: %s""" % (
                newsletter.getUnsubscribe_string(),
                unsubscribe_url,
            )
            settings = get_portal_mail_settings()
            api.portal.send_email(
                recipient=subscriber,
                sender=settings.email_from_address,
                subject=_(u"confirm newsletter unsubscription"),
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

    def unsubscribe(self):
        """
        """
        alsoProvides(self.request, protect.interfaces.IDisableCSRFProtection)
        uid = self.request.get("subscriber")

        newsletter = self.context
        if not INewsletter.providedBy(newsletter):
            api.portal.show_message(
                message=_("Please use the correct unsubscribe url!"),
                request=self.request,
                type="error",
            )
            return self.request.response.redirect(
                api.portal.get_navigation_root(self).absolute_url()
            )

        # We do the deletion as the owner of the newsletter object
        # so that this is possible without login.
        owner = newsletter.getWrappedOwner()
        newSecurityManager(newsletter, owner)
        subscriber = api.content.get(UID=uid)
        if subscriber is None or not INewsletterSubscriber.providedBy(subscriber):
            api.portal.show_message(
                message=_("An error occured"),
                request=self.request,
                type="error",
            )
        else:
            del newsletter[subscriber.id]
            api.portal.show_message(
                message=_("You have been unsubscribed."),
                request=self.request,
                type="info",
            )

        return self.request.response.redirect(
            api.portal.get_navigation_root(self).absolute_url()
        )
