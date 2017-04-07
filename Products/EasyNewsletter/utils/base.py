# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import safe_unicode
from Products.EasyNewsletter.utils.mail import get_email_charset


def safe_portal_encoding(string):
    charset = get_email_charset()
    return safe_unicode(string).encode(charset)
