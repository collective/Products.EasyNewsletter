# -*- coding: utf-8 -*-

from Products.EasyNewsletter import EasyNewsletterMessageFactory as _  # noqa
from zope import schema
from zope.interface import Interface


class IENLSettings(Interface):
    """
    """

    allowed_content_aggregation_types = schema.List(
        required=False,
        title=_(u'Allowed content aggregation types'),
        description=_(
            u'Content types which will be visible in the Content'
            u' aggregation sources reference field.'),
        value_type=schema.TextLine(
            title=_('Content type')
        ),
    )
