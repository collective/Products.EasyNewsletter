# -*- coding: utf-8 -*-

from plone import api
from Products.EasyNewsletter import config
from Products.Five.browser import BrowserView


class Newsletter(BrowserView):
    # template = ViewPageTemplateFile('newsletter.pt')

    def __call__(self):
        self.issues = self.get_send_issues()
        return self.index()

    def get_send_issues(self):
        """ return sended issues brains"""
        enl = self.context.get_newsletter()
        issues = api.content.find(
            portal_type=config.ENL_ISSUE_TYPES,
            review_state='sent',
            sort_on='effective',
            sort_order='reverse',
            path='/'.join(enl.getPhysicalPath())
        )
        return issues
