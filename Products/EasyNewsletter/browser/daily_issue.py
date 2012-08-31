# -*- coding:utf-8 -*-

from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zExceptions import BadRequest

import datetime


class DailyIssueView(BrowserView):
    """Creates a new issue of EasyNewsletter and sends it"""

    def has_content(self):
        return self.context.buildQuery() and self.context.queryCatalog()

    def create_issue(self):
        id = "enlissue_%s" % (datetime.date.today().isoformat())

        try:
            self.context.invokeFactory('ENLIssue', id)
            self.issue = self.context[id]
            self.issue.setTitle(self.context.Title())
            self.issue.loadContent()
            return True

        #If issue already exist, don't create it again
        except BadRequest:
            self.issue = None
            return False

    def send(self):
        if self.issue:
            getMultiAdapter((self.issue, self.context.REQUEST),
                            name="send-issue").send_issue()
            return True
        else:
            return False

    def __call__(self):
        if not self.has_content():
            self.request.response.setStatus(403, 'Nothing to send')
        elif not self.create_issue():
            self.request.response.setStatus(403, 'Already Sent')
        elif self.send():
            self.request.response.setStatus(200)
        else:
            self.request.response.setStatus(500)
        return
