# -*- coding: utf-8 -*-
from Products.EasyNewsletter.interfaces import IENLTemplate
from zope.site.hooks import getSite


def update_enl_template_body_field(obj, event):
    if not IENLTemplate.providedBy(obj):
        return
    portal = getSite()
    issue_template = obj
    template_id = issue_template.getAggregationTemplate()
    if template_id != 'custom':
        template_obj = portal.restrictedTraverse(template_id)
        issue_template.setBody(template_obj.read())
