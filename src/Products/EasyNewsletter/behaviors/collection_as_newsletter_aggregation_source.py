# -*- coding: utf-8 -*-

from plone import schema
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from Products.EasyNewsletter import _
from zope.component import adapter
from zope.interface import implementer, Interface, provider


class ICollectionAsNewsletterAggregationSourceMarker(Interface):
    pass


@provider(IFormFieldProvider)
class ICollectionAsNewsletterAggregationSource(model.Schema):
    """
    """

    model.fieldset(
        "settings",
        label=_(u"Settings"),
        fields=["aggregation_template"],
    )

    aggregation_template = schema.Choice(
        title=_(u"Newsletter aggregation template"),
        description=_(
            u'The <a href="https://productseasynewsletter.readthedocs.io/en/latest/#aggregation-templates">aggregation template</a> used by the Newsletter to render Collection items for the Newsletter.'
        ),
        vocabulary=u"Products.EasyNewsletter.AggregationTemplates",
        # defaultFactory=get_default_aggregation_template,
        required=True,
    )


@implementer(ICollectionAsNewsletterAggregationSource)
@adapter(ICollectionAsNewsletterAggregationSourceMarker)
class CollectionAsNewsletterAggregationSource(object):
    def __init__(self, context):
        self.context = context

    @property
    def aggregation_template(self):
        if hasattr(self.context, "aggregation_template"):
            return self.context.aggregation_template
        return None

    @aggregation_template.setter
    def aggregation_template(self, value):
        self.context.aggregation_template = value
