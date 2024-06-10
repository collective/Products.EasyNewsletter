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
    changed = False
    smtp_host = None
    smtp_port = None
    smtp_userid = None
    smtp_password = None
    if event.record.fieldName == "smtp_host":
        smtp_host = event.newValue
        changed = True
    if event.record.fieldName == "smtp_port":
        smtp_port = event.newValue
        changed = True
    if event.record.fieldName == "smtp_userid":
        smtp_userid = event.newValue
        changed = True
    if event.record.fieldName == "smtp_password":
        smtp_password = event.newValue
        changed = True
    if changed:
        if not smtp_host:
            smtp_host = mailhost.smtp_host
        if not smtp_port:
            smtp_port = mailhost.smtp_port
        if not smtp_userid:
            smtp_userid = mailhost.smtp_userid
        if not smtp_password:
            smtp_password = mailhost.smtp_pwd

        mailhost.manage_makeChanges(
            mailhost.title,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_uid=smtp_userid,
            smtp_pwd=smtp_password,
        )
