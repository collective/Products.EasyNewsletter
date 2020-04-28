# -*- coding: utf-8 -*-

from datetime import datetime
from plone import api
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _  # noqa
from Products.EasyNewsletter.content.newsletter_issue import ISendStatus
from Products.Five.browser import BrowserView


class NewsletterIssueStatistics(BrowserView):
    """Show statistics about a newsletter."""

    failed = 0
    successful = 0
    total = 0

    def __call__(self):
        if 'reset_statistics' in self.request.form:
            status_adapter = ISendStatus(self.context)
            if status_adapter:
                status_adapter.clear()
                api.portal.show_message(
                    message=_('Newsletter issue statistics have been reset.'),
                    request=self.request,
                    type='info',
                )
        return super(NewsletterIssueStatistics, self).__call__()

    def receivers(self):
        status_adapter = ISendStatus(self.context)
        if not status_adapter:
            return
        now = datetime.now()
        records = status_adapter.get_records()
        records = sorted(records, key=lambda x: x.get('status', {}).get('datetime', now))
        self.failed = len(status_adapter.get_keys(successful=False))
        self.successful = len(status_adapter.get_keys(successful=True))
        self.total = len(records)
        return records
