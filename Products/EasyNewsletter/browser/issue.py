# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _
from Products.EasyNewsletter.config import PLACEHOLDERS
from Products.Five.browser import BrowserView
from plone import api
from plone.protect import PostOnly


class IssueView(BrowserView):
    """Single Issue View
    """

    def refresh_issue(self):
        """Refresh the aggregate body when using collections.
        """
        if self.context.getAcquireCriteria():
            self.context.loadContent()
            self.request.response.redirect(self.context.absolute_url())

    def _send_issue_prepare(self):
        self.request['enlwf_guard'] = True
        api.content.transition(obj=self.context, transition='send')
        self.request['enlwf_guard'] = False

    def send_issue(self):
        """
        sets workflow state to sending and then redirects to step2 with UID as
        parameter as simple safety belt.
        """
        PostOnly(self.request)
        if 'test' in self.request.form:  # test must not modify the state
            self.context.send()
            api.portal.show_message(
                message=_("The issue test sending has been initiated."),
                request=self.request,
            )
            return self.request.response.redirect(self.context.absolute_url())

        if self.context.is_send_queue_enabled:
            self._send_issue_prepare()
            self.context.queue_issue_for_sendout()
            api.portal.show_message(
                message=_(
                    "The issue sending has been initiated in the background."
                ),
                request=self.request,
            )
            return self.request.response.redirect(self.context.absolute_url())

        self.send_issue_immediately()

    def send_issue_immediately(self):
        """convinience view for cron and similar

        never call this from UI - needs a way to protect
        currently manager only
        """
        self._send_issue_prepare()
        self.context.send()

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
            draft_id = master_id.lstrip('master_')
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
