# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView


class ProcessQueue(BrowserView):

    def __call__(self):
        import pdb; pdb.set_trace()
        self.context.send()
