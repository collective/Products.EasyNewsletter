# -*- coding: utf-8 -*-

from AccessControl.SecurityManagement import newSecurityManager
from plone import api, protect
from Products.EasyNewsletter import _
from Products.EasyNewsletter.content.newsletter import INewsletter
from Products.EasyNewsletter.content.newsletter_subscriber import INewsletterSubscriber
from Products.Five.browser import BrowserView
from zope.interface import alsoProvides


class NewsletterUnsubscribe(BrowserView):

    def __call__(self):
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
