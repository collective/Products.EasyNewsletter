# -*- coding:utf-8 -*-

from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zExceptions import BadRequest

import datetime


class DailyIssueView(BrowserView):
    """Creates a new issue of EasyNewsletter and sends it"""

    def create_issue(self):
        id = "issue_%s" % (datetime.date.today().isoformat())

        #We don't want an empty issue
        if self.context.buildQuery() and self.context.queryCatalog():
            try:
                self.context.invokeFactory('ENLIssue', id)
                self.issue = self.context[id]
                self.issue.setTitle(self.context.Title())
                return True

            #If issue already exist, don't create it again
            except BadRequest:
                self.issue = None
                return False
        else:
            self.issue = None
            return False

    def send(self):
        if self.issue:
            getMultiAdapter((self.issue, self.context.REQUEST),
                            name="send-issue").send_issue()
        else:
            return None

    def render(self):
        if self.create_issue():
            return self.send()
        else:
            return None
