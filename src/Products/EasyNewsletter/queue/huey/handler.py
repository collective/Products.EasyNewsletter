from zope.interface import implementer
from Products.EasyNewsletter.queue.interfaces import IIssueQueue
from .huey_tasks import send_newsletters


@implementer(IIssueQueue)
class IssueQueue(object):
    def start(self, context):
        """Queues issue for sendout through huey-mini task queue"""
        task_res = send_newsletters(context.UID())
        return task_res
