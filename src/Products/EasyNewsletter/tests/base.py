# -*- coding: utf-8 -*-
from plone import api


def enable_behavior(content_type=None, behavior=None):
    types_tool = api.portal.get_tool('portal_types')
    fti = types_tool.getTypeInfo(content_type)
    behaviors = fti.getProperty('behaviors')
    behaviors = behaviors + (behavior,)
    return fti.manage_changeProperties(behaviors=behaviors)
