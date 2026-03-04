from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides

from Products.Five.browser import BrowserView


class ProcessQueue(BrowserView):
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        self.context.send()
