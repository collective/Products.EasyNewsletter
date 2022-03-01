# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

from Products.EasyNewsletter.config import ENL_EDITHELPER_TYPES


class EditHelperView(BrowserView):
    """ """

    def enable(self):
        return self.context.portal_type in ENL_EDITHELPER_TYPES
