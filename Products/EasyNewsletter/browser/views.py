# -*- coding: utf-8 -*-
# flake8: noqa
from Products.Five import BrowserView


class SubTopicsView(BrowserView):
    """
    """

    @property
    def enl_isOrderable(self):
        try:
            return self.context.portal_interface.objectImplements(
                self.context, 'OFS.OrderSupport.IOrderedContainer')
        except:
            return self.context.portal_interface.objectImplements(
                self.context, 'OFS.OrderSupport.z2IOrderedContainer')
