# -*- coding: utf-8 -*-
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from zope.interface import alsoProvides

from Products.EasyNewsletter import log


class ProcessQueue(BrowserView):
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        log.info("generating and sending newsletter issue emails")
        send_view = api.content.get_view(name="send-issue", context=self.context)
        send_view.send()
