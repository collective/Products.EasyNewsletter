# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView


class NewsletterIssueSendForm(BrowserView):

    def __call__(self):
        return self.index()

    @property
    def sender_name(self):
        newsletter = self.context.get_newsletter()
        return self.request.get('sender_name') or newsletter.sender_name

    @property
    def sender_email(self):
        newsletter = self.context.get_newsletter()
        return self.request.get('sender_email') or newsletter.sender_email

    @property
    def subject(self):
        return self.request.get('subject') or self.context.title

    @property
    def test_receiver(self):
        newsletter = self.context.get_newsletter()
        return self.request.get('test_receiver') or newsletter.test_email
