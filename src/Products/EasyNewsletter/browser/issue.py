# -*- coding: utf-8 -*-
from plone import api
from plone.protect import PostOnly
from plone.protect.interfaces import IDisableCSRFProtection
from Products.CMFPlone.resources import add_resource_on_request
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _  # noqa
from Products.EasyNewsletter.config import IS_PLONE_5
from Products.EasyNewsletter.interfaces import IIssueDataFetcher
from Products.Five.browser import BrowserView
from zope.interface import alsoProvides

import transaction


class IssueView(BrowserView):
    """Single Issue View
    """

    def __call__(self):
        if IS_PLONE_5:
            add_resource_on_request(self.request, 'iframeResizer')
        return super(IssueView, self).__call__()

    @property
    def here_url(self):
        return self.context.absolute_url()

    # TODO: >> new AggregateContent view
    def refresh_issue(self, REQUEST=None):  # noqa
        """Refresh the aggregate body when using collections.
        """
        alsoProvides(self.request, IDisableCSRFProtection)
        self.context.loadContent()
        self.request.response.redirect(self.context.absolute_url())

    # TODO: >> SendIssue view
    def _send_issue_prepare(self):
        self.request['enlwf_guard'] = True
        api.content.transition(obj=self.context, transition='send')
        # commit the transaction so that identical incoming requests, for
        # whatever reason, will not trigger another send
        transaction.commit()
        self.request['enlwf_guard'] = False

    # TODO: >> SendIssue view
    def send_issue(self):
        """
        sets workflow state to sending and then redirects to step2 with UID as
        parameter as simple safety belt.
        """
        PostOnly(self.request)
        if 'test' in self.request.form:  # test must not modify the state
            self.context.send()
            api.portal.show_message(
                message=_('The issue test sending has been initiated.'),
                request=self.request,
            )
            return self.request.response.redirect(self.context.absolute_url())

        if self.context.issue_queue is not None:
            self._send_issue_prepare()
            self.context.queue_issue_for_sendout()
            api.portal.show_message(
                message=_(
                    'The issue sending has been initiated in the background.'
                ),
                request=self.request,
            )
            return self.request.response.redirect(self.context.absolute_url())

        # No queuing but direct send
        self.send_issue_immediately()
        api.portal.show_message(
            message=_(
                'The issue has been generated and sent to the mail server.'
            ),
            request=self.request,
        )
        return self.request.response.redirect(self.context.absolute_url())

    # TODO: >> SendIssueImmediately view
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
        issuedatafetcher = IIssueDataFetcher(self.context)
        preview_html = issuedatafetcher.preview_html()
        return preview_html

    def get_preview(self):
        """ Return the rendered HTML version with all placeholder,
            for admin preview.
        """
        test_receiver = {
            'email': 'john@example.com',
            'fullname': 'John Doe',
            'firstname': 'John',
            'lastname': 'Doe',
            'salutation': 'Dear Mr.',
            'nl_language': 'de',
            'uid': 'xyz',

        }
        issuedatafetcher = IIssueDataFetcher(self.context)
        preview_html = issuedatafetcher.preview_html(
            disable_filter=True, receiver=test_receiver)
        return preview_html

    # BBB: can be removed in 5.x
    def copy_as_draft(self):
        newsletter = self.context.aq_parent
        master_id = self.context.getId()

        if master_id.startswith('master_'):
            draft_id = master_id.replace('master_', '')
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

    # BBB: can be removed in 5.x
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
