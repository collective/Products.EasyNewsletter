# -*- coding: utf-8 -*-

from plone import api
from Products.EasyNewsletter import log


def handler(obj, event):
    """Event handler"""
    mailhost = api.portal.get_tool("MailHost2")
    log.info(
        "Handle IEasyNewsletterControlPanel IRecordEvent for field '{}' to update MailHost2 settings.".format(
            event.record.fieldName
        )
    )
    if event.record.fieldName == "smtp_host":
        mailhost.smtp_host = event.newValue
    if event.record.fieldName == "smtp_port":
        mailhost.smtp_port = event.newValue
    if event.record.fieldName == "smtp_userid":
        mailhost.smtp_userid = event.newValue
    if event.record.fieldName == "smtp_password":
        mailhost.smtp_password = event.newValue
