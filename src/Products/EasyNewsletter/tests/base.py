# -*- coding: utf-8 -*-
from email.header import decode_header
from plone import api
from Products.CMFPlone.utils import safe_unicode

import base64
import cssutils
import email
import logging
import six


cssutils.log.setLevel(logging.CRITICAL)


def enable_behavior(content_type=None, behavior=None):
    types_tool = api.portal.get_tool('portal_types')
    fti = types_tool.getTypeInfo(content_type)
    behaviors = fti.getProperty('behaviors')
    behaviors = behaviors + (behavior,)
    return fti.manage_changeProperties(behaviors=behaviors)


def parsed_payloads_from_msg(msg):
    parsed_msg = email.message_from_string(msg)
    parsed_payloads = dict()
    parsed_payloads['to'] = u"".join([safe_unicode(h[0].strip()) for h in decode_header(parsed_msg.get('To'))])
    parsed_payloads['from'] = u"".join([safe_unicode(h[0].strip()) for h in decode_header(parsed_msg.get('From'))])
    for part in parsed_msg.walk():
        if part.get_content_type():  # in ["text/plain", "text/html"]:
            payload = part.get_payload()
            if not isinstance(payload, six.string_types):
                continue
            parsed_payloads[part.get_content_type()] = base64.b64decode(
                part.get_payload()
            )
    return parsed_payloads
