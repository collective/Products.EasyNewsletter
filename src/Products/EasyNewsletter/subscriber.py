# -*- coding: utf-8 -*-
"""Newsletter subscriber."""

from Products.EasyNewsletter.content.newsletter_issue import ISendStatus


class FilterAlreadySentReceivers(object):
    """Filter all receiver which already got an email in a previous run."""

    def __init__(self, context):
        self.context = context

    def filter(self, receivers):
        status_adapter = ISendStatus(self.context)
        successful = status_adapter.get_keys(successful=True)

        return [
            receiver for receiver in receivers if
            receiver.get('email') not in successful
        ]
