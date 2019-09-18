# -*- coding: utf-8 -*-
from plone import api
from Products.EasyNewsletter import config
from Products.Five.browser import BrowserView


class NewsletterMasters(BrowserView):
    def __call__(self):
        return self.index()

    def get_master_issues(self):
        """ return issues brains of issues in review state master"""
        enl = self.context.get_newsletter()
        issues = api.content.find(
            portal_type=config.ENL_ISSUE_TYPES,
            review_state="master",
            sort_on="modified",
            sort_order="reverse",
            context=enl,
        )
        return issues
