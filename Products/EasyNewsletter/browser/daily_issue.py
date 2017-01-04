# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zExceptions import BadRequest
from zope.component import getMultiAdapter

import datetime


class DailyIssueView(BrowserView):
    """Creates a new issue of EasyNewsletter and sends it"""

    def has_content(self):
        if self.context.buildQuery():
            return len(self.context.queryCatalog())
        else:
            return 0

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
                except BadRequest:
                    # Can't send it twice
                    self.request.response.setStatus(409, 'Already Sent Today')
            else:
                # Empty issue
                self.request.response.setStatus(204, 'Nothing to Send')

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
