# -*- coding: utf-8 -*-

from Products.EasyNewsletter import _
from Products.Five.browser import BrowserView

# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class Newsletter(BrowserView):
    # template = ViewPageTemplateFile('newsletter.pt')

    def __call__(self):
        return self.index()
