# -*- coding: utf-8 -*-
from plone import api
from Products.Five.browser import BrowserView
from zope.interface import Interface
from zope.interface.declarations import implementer


class IENLHelperView(Interface):
    """
    """

    def brain_has_lead_image(self, brain=None):
        """ check if brain has lead image """

    def type_filter(self, items, types=None):
        """ filter given list by portal_type """

    def get_issue(self, context):
        """ return the issue obj """

    def get_results_from_aggregation_sources(self, context):
        """ return a list of result sets based on aggregation sources """


@implementer(IENLHelperView)
class ENLHelperView(BrowserView):
    """ View with some helper methods
    """

    def brain_has_lead_image(self, brain=None):
        has_image = False
        if not brain:
            return
        item_object = brain.getObject()
        # Plone 5:
        has_image = hasattr(item_object.aq_explicit, 'image')
        if has_image and not getattr(item_object.aq_explicit, 'image'):
            return
        # Plone 4:
        if not has_image:
            has_image = hasattr(item_object.aq_explicit, 'tag')
            if not hasattr(item_object.aq_explicit, 'getRawImage'):
                return
            has_image = item_object.getRawImage()
        return has_image

    def type_filter(self, items, types=None):
        """ filter given list by portal_type
        """
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
        """ Returns a list of sources and it's results
        """
        sources = context.getContentSources()
        results = []
        for source in sources:
            sresults = source.queryCatalog()
            if not sresults:
                continue
            results.append({
                'id': source.id,
                'title': source.Title(),
                'description': source.Description(),
                'uid': source.UID(),
                'portal_type': sresults[0].portal_type,
                'brains': sresults,
                'brains_count': len(sresults),
            })
        return results
