# -*- coding: utf-8 -*-
from plone import api
from Products.EasyNewsletter.config import AGG_SOURCES_INFOS
from Products.Five.browser import BrowserView
from zope.annotation import IAnnotations
from zope.interface import Interface
from zope.interface.declarations import implementer


class IENLHelperView(Interface):
    """ """

    def get_scale_util(self, brain=None):
        """
            return the scale_util for a brain's object,
            if the object does not have an image field, return None
        """

    def get_object_url(self, brain):
        """ return object url or None
        """

    def brain_has_lead_image(self, brain=None):
        """check if brain has lead image"""

    def type_filter(self, items, types=None):
        """filter given list by portal_type"""

    def get_issue(self, context):
        """return the issue obj"""

    def get_results_from_aggregation_sources(self, context):
        """return a list of result sets based on aggregation sources"""


@implementer(IENLHelperView)
class ENLHelperView(BrowserView):
    """View with some helper methods"""

    def get_scale_util(self, brain=None):
        if not brain:
            return
        context = brain.getObject()
        has_image = hasattr(context.aq_explicit, "image")
        if not has_image:
            return
        scale_util = api.content.get_view("images", context)
        return scale_util

    def get_object_url(self, brain):
        """ return object url or None
        """
        if not brain:
            return
        return brain.getURL()

    def brain_has_lead_image(self, brain=None):
        has_image = False
        if not brain:
            return
        item_object = brain.getObject()
        # Plone 5:
        has_image = hasattr(item_object.aq_explicit, "image")
        return has_image

    def type_filter(self, items, types=None):
        """filter given list by portal_type"""
        if not types:
            return items
        allowed_items = []
        for item in items:
            if item.portal_type not in types:
                continue
            allowed_items.append(item)
        return allowed_items

    def get_issue(self, context):
        return api.content.get(UID=context.issue_uid)

    def get_results_from_aggregation_sources(self, context):
        """Returns a list of sources and it's results"""
        return self._get_source_infos_from_annotation(context)

    def _get_source_infos_from_annotation(self, context):
        """ """
        annotations = IAnnotations(context)
        if AGG_SOURCES_INFOS not in annotations:
            return []
        return annotations[AGG_SOURCES_INFOS]
