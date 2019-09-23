# -*- coding: utf-8 -*-
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

import datetime
import logging


log = logging.getLogger("Products.EasyNewsletter: daily-issue")


class DailyIssueView(BrowserView):
    """Creates a new issue of EasyNewsletter and sends it"""

    def has_content(self):
        results = []
        enl = self.context
        sources = enl.content_aggregation_sources
        for source in sources:
            source = source.to_object
            source_results = source.queryCatalog()
            results.extend(source_results)
        return len(results)

    def __generate_id(self):
        return "enlissue_%s" % (datetime.date.today().isoformat())

    def already_sent(self):
        if self.__generate_id() in self.context:
            return True
        else:
            return False

    def create_issue(self):
        id = self.__generate_id()

        try:
            self.issue = api.content.create(type='Newsletter Issue', id=id, container=self.context)
        # If issue already exist, don't create it again
        except BadRequest:
            raise

        self.issue.title = self.context.title
        self.issue.description = self.context.description

        # workaround because of this:
        # https://community.plone.org/t/icontextawaredefaultfactory-has-wrong-context-and-no-acquisition-chain-if-called-in-python/9119
        self.issue.prologue = safe_unicode(self.context.default_prologue)
        self.issue.epilogue = safe_unicode(self.context.default_epilogue)
        self.issue.content_aggregation_sources = self.context.content_aggregation_sources
        self.issue.output_template = self.context.output_template

        # aggregate content for issue:
        getMultiAdapter(
            (self.issue, self.context.REQUEST),
            name="aggregate-content"
        )()

    def send(self):
        if self.issue:
            getMultiAdapter(
                (self.issue, self.context.REQUEST),
                name="send-issue"
            ).send_issue_immediately()

    def __call__(self):
        if self.request["REQUEST_METHOD"] == "POST":
            alsoProvides(self.request, IDisableCSRFProtection)
            if self.has_content():
                try:
                    self.create_issue()
                    # Accepted. Sending mails
                    self.send()
                    self.request.response.setStatus(200)
                    log.info("Daily issue sended.")
                except BadRequest:
                    # Can't send it twice
                    self.request.response.setStatus(409, 'Already Sent Today')
                    log.info("Daily issue already send today, skip!")
            else:
                # Empty issue
                self.request.response.setStatus(204, 'Nothing to Send')
                log.info("No data found for daily issue today, skip!")

        elif self.request["REQUEST_METHOD"] == "GET":
            if self.already_sent():
                self.request.response.setStatus(200, 'Already Sent Today')
            elif not self.has_content():
                self.request.response.setStatus(204, 'Nothing to Send')
            else:
                self.request.response.setStatus(100, 'Not sent yet')
        else:
            self.request.response.setStatus(405)
            self.request.response.setHeader("Allow", "GET, POST")


class TriggerDailyIssueView(BrowserView):
    """
    """

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        self.request['REQUEST_METHOD'] = 'POST'
        view = getMultiAdapter(
            (self.context, self.request),
            name="daily-issue")
        return view()
