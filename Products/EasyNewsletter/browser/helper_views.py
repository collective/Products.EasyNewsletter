# -*- coding: utf-8 -*-
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
        print(allowed_items)
        return allowed_items
