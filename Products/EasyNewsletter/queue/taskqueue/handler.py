# -*- coding: utf-8 -*-
from collective.taskqueue import taskqueue
from Products.EasyNewsletter.queue.interfaces import IIssueQueue
from zope.interface import implementer

QUEUE_NAME = 'Products.EasyNewsletter.queue'
VIEW_NAME = 'enl_taskqueue_sendout'


@implementer(IIssueQueue)
class TCIssueQueue(object):

    def start(self, context):
        """Queues issue for sendout through collective.taskqueue
        """
        jobid = taskqueue.add(
            '/'.join(context.getPhysicalPath() + (VIEW_NAME, )),
            queue=QUEUE_NAME
        )
        return jobid
