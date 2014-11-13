# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup
from Products.CMFCore.utils import getToolByName
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _
from Products.EasyNewsletter.config import PLACEHOLDERS
from Products.Five.browser import BrowserView
from plone import api


class IssueView(BrowserView):
    """
    """

    def refresh_issue(self):
        """Refresh the aggregate body when using collections.
        """
        if self.context.getAcquireCriteria():
            self.context.loadContent()
            self.request.response.redirect(self.context.absolute_url())

    def send_issue(self):
        """
        """
        putils = getToolByName(self.context, "plone_utils")
        self.context.send()
        putils.addPortalMessage(_("The issue has been send."))
        return self.request.response.redirect(self.context.absolute_url())

    def get_public_body(self):
        """ Return the rendered HTML version without placeholders.
        """
        html = self.context._render_output_html()
        for placeholder in PLACEHOLDERS:
            html = html.replace('[[' + placeholder + ']]', '')
        soup = BeautifulSoup(html)
        for node in soup.findAll('div', {'class': 'mailonly'}):
            node.extract()
        return soup.renderContents()

    def copy_as_draft(self):
        newsletter = self.context.aq_parent
        master_id = self.context.getId()

        if master_id.startswith('master_'):
            draft_id = master_id.strip('master_')
        else:
            draft_id = master_id

        draft_obj = api.content.copy(
            source=self.context,
            target=newsletter,
            safe_id=True,
            id=draft_id
        )

        return self.request.response.redirect(
            draft_obj.absolute_url() + '/edit'
        )

    def copy_as_master(self):
        request = self.context.REQUEST
        newsletter = self.context.aq_parent
        master_id = "master_" + self.context.getId()

        master_obj = api.content.copy(
            source=self.context,
            target=newsletter,
            safe_id=True,
            id=master_id
        )

        request['enlwf_guard'] = True
        api.content.transition(obj=master_obj, transition='make_master')
        request['enlwf_guard'] = False

        return self.request.response.redirect(
            master_obj.absolute_url() + '/edit'
        )
