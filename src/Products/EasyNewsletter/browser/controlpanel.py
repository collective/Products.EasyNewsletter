# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import Interface

from Products.EasyNewsletter import EasyNewsletterMessageFactory as _  # noqa


class IENLSettings(Interface):
    """ """

    allowed_content_aggregation_types = schema.List(
        required=False,
        title=_("Allowed content aggregation types"),
        description=_(
            "Content types which will be visible in the Content"
            " aggregation sources reference field."
        ),
        value_type=schema.TextLine(title=_("Content type")),
    )
