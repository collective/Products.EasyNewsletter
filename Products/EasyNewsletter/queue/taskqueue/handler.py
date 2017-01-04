# -*- coding: utf-8 -*-
from plone import api
from Producer.EasyNewsletter.queue.interfaces import IIssueQueue
from Producer.EasyNewsletter.queue.interfaces import Progress
from zope.interface import implementer


@implementer(IIssueQueue)
class TCIssueQueue(object):

    def start(self, context):
        """Queues issue for sendout through collective.taskqueue
        """
        api.content.get_uuid(context)

    def progress(self, context):
        return Progress(None, None, None)
