# -*- coding: utf-8 -*-
from collective.zamqp.consumer import Consumer
from collective.zamqp.interfaces import IProducer
from collective.zamqp.producer import Producer
from plone import api
from Products.EasyNewsletter.queue.interfaces import IIssueQueue
from zope.component import getUtility
from zope.interface import implementer, Interface


QUEUE_NAME = 'Products.EasyNewsletter.queue'


class IMailProcessingMessage(Interface):
    """Marker interface for Mail processing  message"""


class MailProcessingProducer(Producer):
    """Produces Mail processing tasks"""

    connection_id = 'superuser'
    serializer = 'msgpack'
    queue = QUEUE_NAME
    routing_key = QUEUE_NAME

    durable = True


class MailProcessingConsumer(Consumer):
    """Consumes Mail processing tasks"""

    connection_id = 'superuser'
    marker = IMailProcessingMessage
    queue = QUEUE_NAME
    routing_key = QUEUE_NAME

    durable = True


def process_message(message, event):
    """Handle messages received through consumer."""
    uuid = message.header_frame.correlation_id
    context = api.content.get(UID=uuid)

    # send out emails
    context.send()

    # Send ACK
    message.ack()


@implementer(IIssueQueue)
class ZAMQPIssueQueue(object):

    def start(self, context):
        """Queues issue for sendout through collective.zamqp.
        """
        kwargs = {}
        producer = getUtility(IProducer, name=QUEUE_NAME)
        producer.register()
        producer.publish(kwargs, correlation_id=api.content.get_uuid(context))
