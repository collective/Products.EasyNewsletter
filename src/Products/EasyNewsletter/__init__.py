# -*- coding: utf-8 -*-
# avoid circular import
# from Products.EasyNewsletter import config  # noqa
import logging
import threading

from huey.bin.huey_consumer import load_huey
from huey.consumer_options import ConsumerConfig
from zope.i18nmessageid import MessageFactory

log = logging.getLogger("Products.EasyNewsletter")

EasyNewsletterMessageFactory = MessageFactory("Products.EasyNewsletter")
_ = EasyNewsletterMessageFactory

consumer_options = {
    "backoff": 1.15,
    "check_worker_health": True,
    "extra_locks": None,
    "flush_locks": False,
    "health_check_interval": 10,
    "initial_delay": 0.1,
    "max_delay": 10.0,
    "periodic": True,
    "scheduler_interval": 1,
    "worker_type": "thread",
    "workers": 1,
    "logfile": "huey.log",
    "verbose": False,
}

h = load_huey("Products.EasyNewsletter.queue.huey.huey_tasks.huey")

cconfig = ConsumerConfig(**consumer_options)
cconfig.validate()
cconfig.setup_logger()
cconsumer = h.create_consumer(**cconfig.values)

th = threading.Thread(target=cconsumer.run)
th.start()
