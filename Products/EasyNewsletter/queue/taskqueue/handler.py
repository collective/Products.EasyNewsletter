# -*- coding: utf-8 -*-
from collective.taskqueue import taskqueue
from Products.EasyNewsletter.queue.interfaces import IIssueQueue
from zope.interface import implementer

QUEUE_NAME = 'enl'
VIEW_NAME = 'enl_taskqueue_sendout'


@implementer(IIssueQueue)
class TCIssueQueue(object):

    def start(self, context):
        """Queues issue for sendout through collective.taskqueue
        """
        '/'.join(context.getPhysicalPath() + [VIEW_NAME])
        taskqueue.add(
            '/'.join(context.getPhysicalPath()),
            queue=QUEUE_NAME
        )
