# -*- coding: utf-8 -*-
from plone import api
from collective.taskqueue2.huey_tasks import schedule_browser_view
from Products.EasyNewsletter.queue.interfaces import IIssueQueue
from zope.interface import implementer


QUEUE_NAME = "Products.EasyNewsletter.queue"
ENL_VIEW_NAME = "enl_taskqueue_sendout"


@implementer(IIssueQueue)
class TCIssueQueue(object):
    def start(self, context):
        """Queues issue for sendout through collective.taskqueue"""
        # import pdb; pdb.set_trace()  # NOQA: E702
        result = schedule_browser_view(
            view_name=ENL_VIEW_NAME,
            context_path="/".join(context.getPhysicalPath()),
            site_path="/".join(api.portal.get().getPhysicalPath()),
            username=api.user.get_current().getId(),
            params=dict(
                base=context.REQUEST.base,
                layers=context.REQUEST.__provides__,
                cookies=context.REQUEST.cookies,
                form=dict(),
                _plonebrowserlayer_=context.REQUEST._plonebrowserlayer_,
                _plonetheme_=context.REQUEST._plonetheme_,
            ),
        )
        # jobid = taskqueue.add(
        #     "/".join(context.getPhysicalPath() + (VIEW_NAME,)), queue=QUEUE_NAME
        # )
        return result
