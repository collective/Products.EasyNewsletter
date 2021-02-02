# -*- coding: utf-8 -*-

from plone.dexterity.interfaces import IDexterityContent
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


class VocabItem(object):
    def __init__(self, token, value):
        self.token = token
        self.value = value


@implementer(IVocabularyFactory)
class AggregationTemplates(object):
    """
    """

    def __call__(self, context):
        items = []

        registry = getUtility(IRegistry)
        aggregation_templates = registry.get(
            'Products.EasyNewsletter.content_aggregation_templates')
        for key, value in aggregation_templates.items():
            items.append(VocabItem(key, value))

        # Fix context if you are using the vocabulary in DataGridField.
        # See https://github.com/collective/collective.z3cform.datagridfield/issues/31:  # NOQA: 501
        if not IDexterityContent.providedBy(context):
            req = getRequest()
            context = req.PARENTS[0]

        # create a list of SimpleTerm items:
        terms = []
        for item in items:
            terms.append(
                SimpleTerm(
                    value=item.token,
                    token=str(item.token),
                    title=item.value,
                )
            )
        # Create a SimpleVocabulary from the terms list and return it:
        return SimpleVocabulary(terms)


AggregationTemplatesFactory = AggregationTemplates()
