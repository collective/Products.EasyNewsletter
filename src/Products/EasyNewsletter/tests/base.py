# -*- coding: utf-8 -*-
from plone import api

import base64
import email
import six


def enable_behavior(content_type=None, behavior=None):
    types_tool = api.portal.get_tool('portal_types')
    fti = types_tool.getTypeInfo(content_type)
    behaviors = fti.getProperty('behaviors')
    behaviors = behaviors + (behavior,)
    return fti.manage_changeProperties(behaviors=behaviors)


def parsed_payloads_from_msg(msg):
    parsed_msg = email.message_from_string(msg)
    parsed_payloads = dict()
    for part in parsed_msg.walk():
        if part.get_content_type():  # in ["text/plain", "text/html"]:
            payload = part.get_payload()
            if not isinstance(payload, six.string_types):
                continue
            parsed_payloads[part.get_content_type()] = base64.b64decode(
                part.get_payload()
            )
    return parsed_payloads
