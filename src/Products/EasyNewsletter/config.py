# -*- coding: utf-8 -*-
# flake8: noqa

from plone import api
from Products.EasyNewsletter import _
from zope.i18nmessageid import MessageFactory

import re


# see __init__.py
# _ = MessageFactory('Products.EasyNewsletter')

PROJECTNAME = "EasyNewsletter"

ENL_ISSUE_TYPES = ["ENLIssue", "Newsletter Issue"]
ENL_EDITHELPER_TYPES = ["EasyNewsletter", "ENLIssue", "Newsletter", "Newsletter Issue"]

PLACEHOLDERS = ["UNSUBSCRIBE", "SUBSCRIBER_SALUTATION"]

AGG_SOURCES_INFOS = "agg_sources_infos"

SALUTATION = {
    "ms": _("label_salutation_ms", "Ms."),
    "mr": _("label_salutation_mr", "Mr."),
}

# NL_LANGUAGE = DisplayList((
#     ('', _(u'label_choose_nl_language', 'Choose language...')),
#     ('de', _(u'label_salutation_de', 'DE')),
#     ('en', _(u'label_salutation_en', 'EN')),
#     ('fr', _(u'label_salutation_fr', 'FR')),
# ))

MESSAGE_CODE = {
    "email_added": _(
        "email_added",
        default="Your email has been registered. A confirmation email was"
        " sent to your address. Please check your inbox and click "
        " on the link in the email in order to confirm your"
        " subscription.",
    ),
    "invalid_email": _("invalid_email", default="Please enter a valid email address."),
    "email_exists": _(
        "email_exists", default="Your email address is already registered."
    ),
    "invalid_hashkey": _(
        "invalid_hashkey", default="Please enter a valid email address."
    ),
    "subscription_confirmed": _(
        "subscription_confirmed",
        default="Your subscription was successfully confirmed.",
    ),
}


EMAIL_RE = re.compile(
    r"(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,63}(?:\s|$)", re.IGNORECASE
)


DEFAULT_SUBSCRIBER_CONFIRMATION_MAIL_SUBJECT = _(
    "Confirm your subscription on ${portal_url}"
)

DEFAULT_SUBSCRIBER_CONFIRMATION_MAIL_TEXT = """\
You subscribe to the ${newsletter_title}.\n\n
Your registered email is: ${subscriber_email}\n
Please click on the link to confirm your subscription: \n
${confirmation_url}"""
