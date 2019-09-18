# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView


class Newsletter(BrowserView):
    # template = ViewPageTemplateFile('newsletter.pt')

    def __call__(self):
        return self.index()
