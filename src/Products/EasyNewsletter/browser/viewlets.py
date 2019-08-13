# -*- coding: utf-8 -*-
from plone.app.layout.viewlets.common import ViewletBase


class ENLActionsViewlet(ViewletBase):

    def update(self):
        """
        """
        self.id = self.context.id
        self.enl_url = self.context.absolute_url()
