# -*- coding: utf-8 -*-
# from Products.EasyNewsletter.config import IS_PLONE_5
from plone.registry.interfaces import IRegistry
from Products.EasyNewsletter.browser.controlpanel import IENLSettings
from zope.component import getUtility
from zope.interface import Interface


class IENLUtils(Interface):
    """ ENL utils methods
    """


class ENLUtils(object):
    """ ENL utils methods
    """

    def get_allowed_content_aggregation_types(self):
        """ return a tuple of allowed content types for content aggregation
        """
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            IENLSettings, prefix='Products.EasyNewsletter')
        return settings.allowed_content_aggregation_types
