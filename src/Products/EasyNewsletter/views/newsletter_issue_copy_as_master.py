# -*- coding: utf-8 -*-
from plone import api
from Products.Five.browser import BrowserView


class NewsletterIssueCopyAsMaster(BrowserView):
    def __call__(self):
        return self.copy_as_master()

    def copy_as_master(self):
        request = self.request
        newsletter = self.context.get_newsletter()
        master_id = "master_" + self.context.id

        master_obj = api.content.copy(
            source=self.context, target=newsletter, safe_id=True, id=master_id
        )

        request["enlwf_guard"] = True
        api.content.transition(obj=master_obj, transition="make_master")
        request["enlwf_guard"] = False

        return self.request.response.redirect(master_obj.absolute_url() + "/edit")
