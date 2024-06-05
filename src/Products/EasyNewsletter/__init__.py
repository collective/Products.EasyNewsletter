# -*- coding: utf-8 -*-
# avoid circular import
# from Products.EasyNewsletter import config  # noqa
from zope.i18nmessageid import MessageFactory

import logging

log = logging.getLogger("Products.EasyNewsletter")

EasyNewsletterMessageFactory = MessageFactory("Products.EasyNewsletter")
_ = EasyNewsletterMessageFactory
