# -*- coding: utf-8 -*-
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from zope.interface import alsoProvides

from Products.EasyNewsletter import log


class ProcessQueue(BrowserView):
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        log.info("start sending:\n")
        import pdb; pdb.set_trace()  # NOQA: E702`c`
        # send_view = api.content.get_view(name="send-issue", context=self.context)
        send_view = self.context.restrictedTraverse("send-issue")
        send_view.send()
        log.info("sending done ;)\n")
