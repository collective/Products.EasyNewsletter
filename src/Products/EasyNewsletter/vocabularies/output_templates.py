# -*- coding: utf-8 -*-

from plone.dexterity.interfaces import IDexterityContent
# from plone import api
from plone.registry.interfaces import IRegistry
from Products.EasyNewsletter import _
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
class OutputTemplates(object):
    """
    """

    def __call__(self, context):
        items = []

        registry = getUtility(IRegistry)
        output_templates = registry.get("Products.EasyNewsletter.output_templates")
        for key, value in output_templates.items():
            items.append(VocabItem(key, value))
        if not len(items):
            items.append(
                VocabItem(
                    u"output_default",
                    _(u"enl_label_default_output_template", u"Default output template"),
                )
            )

        # Fix context if you are using the vocabulary in DataGridField.
        # See https://github.com/collective/collective.z3cform.datagridfield/issues/31:  # NOQA: 501
        if not IDexterityContent.providedBy(context):
            req = getRequest()
            context = req.PARENTS[0]

        # create a list of SimpleTerm items:
        terms = []
        for item in items:
            terms.append(
                SimpleTerm(value=item.token, token=str(item.token), title=item.value)
            )
        # Create a SimpleVocabulary from the terms list and return it:
        return SimpleVocabulary(terms)


OutputTemplatesFactory = OutputTemplates()
