# -*- coding: utf-8 -*-
"""Newsletter subscriber."""

from Products.DCWorkflow.interfaces import IAfterTransitionEvent
from Products.EasyNewsletter.content.newsletter_issue import (
    INewsletterIssue,
    ISendStatus,
)
from zope.component import adapter


class FilterAlreadySentReceivers(object):
    """Filter all receiver which already got an email in a previous run."""

    def __init__(self, context):
        self.context = context

    def filter(self, receivers):
        status_adapter = ISendStatus(self.context)
        if not status_adapter:
            return receivers
        successful = status_adapter.get_keys(successful=True)

        return [
            receiver for receiver in receivers if
            receiver.get('email') not in successful
        ]


@adapter(IAfterTransitionEvent)
def reset_send_status(event):
    if not INewsletterIssue.providedBy(event.object):
        return
    if event.new_state.id in ['master']:
        status_adapter = ISendStatus(event.object)
        if not status_adapter:
            return
        status_adapter.clear()
    return
