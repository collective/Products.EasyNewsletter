# -*- coding: utf-8 -*-

from plone.app.layout.viewlets import ViewletBase


class NewsletterActions(ViewletBase):

    def update(self):
        """
        """
        self.id = self.context.id
        self.enl_url = self.context.absolute_url()
        self.view_name = self.view.__name__

    def render(self):
        return super(NewsletterActions, self).render()
