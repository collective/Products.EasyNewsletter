# -*- coding: utf-8 -*-

from plone import api
from Products.EasyNewsletter import log
from Products.MailHost.interfaces import IMailHost
from Products.MailHost.MailHost import MailHost
from zope.component import getSiteManager


ENL_MAILHOST_NAME = "MailHost2"


def handler(obj, event):
    """Event handler"""
    try:
        mailhost = api.portal.get_tool(ENL_MAILHOST_NAME)
    except api.exc.InvalidParameterError:
        mailhost = MailHost(
            id=ENL_MAILHOST_NAME,
            title="Alternative email server settings for Newsletters",
            smtp_host="",
            smtp_port=25,
            smtp_uid="",
            smtp_pwd="",
            force_tls=False,
        )
        portal = api.portal.get()
        portal._setObject(ENL_MAILHOST_NAME, mailhost)
        sm = getSiteManager(context=portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)
    log.info(
        "Handle IEasyNewsletterControlPanel IRecordEvent for field '{}' to update {} settings.".format(
            event.record.fieldName, ENL_MAILHOST_NAME
        )
    )
    if event.record.fieldName == "smtp_host":
        mailhost.smtp_host = event.newValue
    if event.record.fieldName == "smtp_port":
        mailhost.smtp_port = event.newValue
    if event.record.fieldName == "smtp_userid":
        mailhost.smtp_uid = event.newValue
    if event.record.fieldName == "smtp_password":
        mailhost.smtp_pwd = event.newValue
