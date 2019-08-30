# -*- coding: utf-8 -*-

from plone import api
from plone.protect import PostOnly
from plone.protect.interfaces import IDisableCSRFProtection
from Products.CMFPlone.resources import add_resource_on_request
from Products.EasyNewsletter import _  # noqa
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _
from Products.EasyNewsletter.config import IS_PLONE_5
from Products.EasyNewsletter.interfaces import IIssueDataFetcher
from Products.Five.browser import BrowserView


class NewsletterIssue(BrowserView):
    def __call__(self):
        add_resource_on_request(self.request, "iframeResizer")
        return self.index()

    @property
    def here_url(self):
        return self.context.absolute_url()

    def refresh_issue(self, REQUEST=None):  # noqa
        """Refresh the aggregate body when using collections.
        """
        alsoProvides(self.request, IDisableCSRFProtection)
        self.context.loadContent()
        self.request.response.redirect(self.context.absolute_url())
