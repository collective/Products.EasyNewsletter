# -*- coding: utf-8 -*-

from plone import api
from Products.Five.browser import BrowserView


class NewsletterIssueCopyAsDraft(BrowserView):
    def __call__(self):
        return self.copy_as_draft()

    def copy_as_draft(self):
        newsletter = self.context.get_newsletter()
        master_id = self.context.id

        if master_id.startswith("master_"):
            draft_id = master_id.replace("master_", "")
        else:
            draft_id = master_id

        draft_obj = api.content.copy(
            source=self.context, target=newsletter, safe_id=True, id=draft_id
        )

        return self.request.response.redirect(draft_obj.absolute_url() + "/edit")
