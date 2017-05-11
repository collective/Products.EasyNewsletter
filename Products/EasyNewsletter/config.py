# -*- coding: utf-8 -*-
# flake8: noqa

from Products.Archetypes.atapi import DisplayList
from zope.i18nmessageid import MessageFactory
from plone import api

import re

_ = MessageFactory('EasyNewsletter')

IS_PLONE_5 = api.env.plone_version().startswith('5')
IS_PLONE_4 = api.env.plone_version().startswith('4')

PROJECTNAME = 'EasyNewsletter'

ENL_ISSUE_TYPES = ['ENLIssue']
ENL_EDITHELPER_TYPES = ['EasyNewsletter', 'ENLIssue']

PLACEHOLDERS = ['UNSUBSCRIBE', 'SUBSCRIBER_SALUTATION']


SALUTATION = DisplayList((
    ('', _(u'label_choose_saluation', 'Choose salutation...')),
    ('ms', _(u'label_salutation_ms', 'Ms.')),
    ('mr', _(u'label_salutation_mr', 'Mr.')),
))

NL_LANGUAGE = DisplayList((
    ('', _(u'label_choose_nl_language', 'Choose language...')),
    ('de', _(u'label_salutation_de', 'DE')),
    ('en', _(u'label_salutation_en', 'EN')),
    ('fr', _(u'label_salutation_fr', 'FR')),
))

MESSAGE_CODE = {
    'email_added': _(
        u'email_added',
        default=u'Your email has been registered. A confirmation email was'
                u' sent to your address. Please check your inbox and click '
                u' on the link in the email in order to confirm your'
                u' subscription.'
    ),
    'invalid_email': _(
        u'invalid_email', default=u'Please enter a valid email address.'),
    'email_exists': _(
        u'email_exists', default=u'Your email address is already registered.'),
    'invalid_hashkey': _(
        u'invalid_hashkey', default=u'Please enter a valid email address.'),
    'subscription_confirmed': _(
        u'subscription_confirmed',
        default=u'Your subscription was successfully confirmed.'),
}


EMAIL_RE = re.compile(
    r"(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)", re.IGNORECASE)


DEFAULT_SUBSCRIBER_CONFIRMATION_MAIL_SUBJECT = _(
    u'Confirm your subscription on ${portal_url}'
)

DEFAULT_SUBSCRIBER_CONFIRMATION_MAIL_TEXT = """\
You subscribe to the ${newsletter_title}.\n\n
Your registered email is: ${subscriber_email}\n
Please click on the link to confirm your subscription: \n
${confirmation_url}"""
