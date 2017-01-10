# -*- coding: utf-8 -*-
from collections import namedtuple
from zope.interface import Interface

# expected types: sent=int, total=int, start=datetime
Progress = namedtuple('Progress', ['sent', 'total', 'start'])


class IIssueQueue(Interface):
    """ Queues an issue into a queue
    """

    def start(issue):
        """Queues an IENLissue for sendout
        """
