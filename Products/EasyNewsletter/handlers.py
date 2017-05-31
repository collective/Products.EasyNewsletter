# -*- coding: utf-8 -*-
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from plone import api
from Products.EasyNewsletter.interfaces import IEasyNewsletter


def add_default_enl_templates(obj, event):
    if not IEasyNewsletter.providedBy(obj):
        return
    if not hasattr(obj, '_at_uid'):
        return

    def create_template(id="", title=""):
        """ Add template object """
        if getattr(obj, id, None):
            print("alread exists: %s" % id)
            return
        api.content.create(
            container=obj, type='ENLTemplate', id=id, title=title)
        obj[id].setAggregationTemplate(id)

    registry = getUtility(IRegistry)
    aggregation_templates = registry.get(
        'Products.EasyNewsletter.content_aggregation_templates')
    if not aggregation_templates:
        return
    for key, value in aggregation_templates.items():
        tmpl_id = str(key)
        create_template(id=tmpl_id, title=value)
