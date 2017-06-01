# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zExceptions import BadRequest
from zope.component import getMultiAdapter
import datetime
import logging


log = logging.getLogger("Products.EasyNewsletter: daily-issue")


class DailyIssueView(BrowserView):
    """Creates a new issue of EasyNewsletter and sends it"""

    def has_content(self):
        results = []
        enl = self.context
        enl_template_id = enl.getTemplate()
        if enl_template_id not in self.context.objectIds():
            return
        enl_template = getattr(enl.aq_explicit, enl_template_id, None)
        sources = enl_template.getContentSources()
        for source in sources:
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
            self.context.invokeFactory('ENLIssue', id)
        # If issue already exist, don't create it again
        except BadRequest:
            raise

        self.issue = self.context[id]
        self.issue.setTitle(self.context.Title())
        self.issue.setDescription(self.context.Description())
        self.issue.loadContent()

    def send(self):
        if self.issue:
            getMultiAdapter(
                (self.issue, self.context.REQUEST),
                name="send-issue"
            ).send_issue_immediately()

    def __call__(self):

        if self.request["REQUEST_METHOD"] == "POST":
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
        self.request['REQUEST_METHOD'] = 'POST'
        view = getMultiAdapter(
            (self.context, self.request),
            name="daily-issue")
        return view()
