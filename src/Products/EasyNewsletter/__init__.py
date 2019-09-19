# -*- coding: utf-8 -*-
from Products.CMFCore import utils as cmfutils
# avoid circular import
from Products.EasyNewsletter import config  # noqa
from zope.i18nmessageid import MessageFactory


EasyNewsletterMessageFactory = MessageFactory('EasyNewsletter')
_ = EasyNewsletterMessageFactory
