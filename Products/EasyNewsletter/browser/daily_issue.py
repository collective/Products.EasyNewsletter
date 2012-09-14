# -*- coding:utf-8 -*-

from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zExceptions import BadRequest

import datetime


class DailyIssueView(BrowserView):
    """Creates a new issue of EasyNewsletter and sends it"""

    def has_content(self):
        if self.context.buildQuery():
            return len(self.context.queryCatalog())
        else:
            return 0

    def create_issue(self):
        id = "enlissue_%s" % (datetime.date.today().isoformat())

        try:
            self.context.invokeFactory('ENLIssue', id)
        #If issue already exist, don't create it again
        except BadRequest:
            raise

        self.issue = self.context[id]
        self.issue.setTitle(self.context.Title())
        self.issue.loadContent()

    def send(self):
        if self.issue:
            getMultiAdapter((self.issue, self.context.REQUEST),
                            name="send-issue").send_issue()

    def __call__(self):
        if self.has_content():
            try:
                self.create_issue()

                # Accepted. Sending mails
                self.send()
                self.request.response.setStatus(200)
            except BadRequest:
                # Can't send it twice
                self.request.response.setStatus(403, 'Already Sent')
        else:
            # Empty issue
            self.request.response.setStatus(204, 'Nothing to send')
