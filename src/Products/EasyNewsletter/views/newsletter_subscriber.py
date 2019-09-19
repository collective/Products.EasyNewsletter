# -*- coding: utf-8 -*-

from Products.EasyNewsletter import _
from Products.Five.browser import BrowserView


class NewsletterSubscriber(BrowserView):
    # If you want to define a template here, please remove the template from
    # the configure.zcml registration of this view.
    # template = ViewPageTemplateFile('newsletter_subscriber.pt')

    def __call__(self):
        # Implement your own actions:
        self.msg = _(u'A small message')
        return self.index()
