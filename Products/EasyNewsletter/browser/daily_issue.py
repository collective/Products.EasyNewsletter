# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.site.hooks import getSite
import transaction
import datetime


class DailyIssueView(BrowserView):
    """Creates a new issue of EasyNewsletter and sends it"""

    def has_content(self):
        results = []
        portal = getSite()
        enl_template_id = self.context.getTemplate()
        if enl_template_id not in self.context.objectIds():
            return
        enl_template = self.context.getattr(enl_template_id, None)

        # here we create a write on read, but we do not need to persist it:
        sp = transaction.savepoint()
        enl_template.setIssue(self.context.UID())
        template_id = enl_template.getAggregationTemplate()
        if template_id != 'custom':
            template_obj = portal.restrictedTraverse(template_id)
            # XXX we copy over the template here every time we load the content
            # which is not perfect but ok for now.
            # This will be refactored when we drop Plone 4 support and use
            # behaviors on source object like Collections
            enl_template.setBody(template_obj.read())
        sources = enl_template.getContentSources()
        for source in sources:
            source_results = source.queryCatalog()
            results.extend(source_results)

        sp.rollback()
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
