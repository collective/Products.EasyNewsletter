# -*- coding: utf-8 -*-
from Products.EasyNewsletter.config import ENL_EDITHELPER_TYPES
from Products.Five.browser import BrowserView


class EditHelperView(BrowserView):
    """
    """
    def enable(self):
        return self.context.portal_type in ENL_EDITHELPER_TYPES
