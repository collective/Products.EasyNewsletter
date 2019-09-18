# -*- coding: utf-8 -*-
from plone import api
from plone.app.layout.viewlets import ViewletBase


class NewsletterActions(ViewletBase):

    def update(self):
        """
        """
        self.id = self.context.id
        self.enl_url = self.context.absolute_url()
        self.view_name = self.view.__name__

    def render(self):
        if not api.user.is_anonymous():
            return super(NewsletterActions, self).render()
        else:
            return u""
