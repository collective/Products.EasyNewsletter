# -*- coding: utf-8 -*-
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from zope.component import getUtility
from zope.interface import Interface


class IPortalMailSettings(Interface):
    """ PortalMailSettings proxy interface
    """


class PortalMailSettings(object):
    """ PortalMailSettings proxy
    """

    def __init__(self):
        self.settings = {}

    def __getattr__(self, key):
        self.registry = getUtility(IRegistry)
        reg_mail = self.registry.forInterface(
            IMailSchema, prefix='plone')
        self.settings['smtp_host'] = reg_mail.smtp_host
        self.settings['smtp_port'] = reg_mail.smtp_port
        self.settings['smtp_userid'] = reg_mail.smtp_userid
        self.settings['smtp_pass'] = reg_mail.smtp_pass
        self.settings['email_from_address'] = reg_mail.email_from_address
        self.settings['email_from_name'] = reg_mail.email_from_name
        self.settings['email_charset'] = reg_mail.email_charset
        return self.settings.get(key)


def get_portal_mail_settings():
    return PortalMailSettings()


def get_email_charset():
    registry = getUtility(IRegistry)
    return registry.get('plone.email_charset', 'utf-8')
