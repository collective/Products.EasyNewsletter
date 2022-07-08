# -*- coding: utf-8 -*-

from plone import api
# from Products.EasyNewsletter import _
from Products.EasyNewsletter import config
from Products.Five.browser import BrowserView


class NewsletterDrafts(BrowserView):
    def __call__(self):
        return self.index()

    @property
    def draft_issues(self):
        return api.content.find(
            portal_type=config.ENL_ISSUE_TYPES,
            review_state=["draft", "sending"],
            sort_on="modified",
            sort_order="reverse",
            context=self.context,
        )
