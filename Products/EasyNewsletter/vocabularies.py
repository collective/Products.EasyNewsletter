# -*- coding: utf-8 -*-

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from Products.EasyNewsletter.interfaces import IEasyNewsletter
from zope.interface import implementer
from plone import api


@implementer(IVocabularyFactory)
class NewslettersVocabulary(object):
    """Provide available newsletters."""

    def __call__(self, context):
        terms = []
        newsletters = api.content.find(object_provides=IEasyNewsletter)
        for newsletter in newsletters:
            terms.append(
                SimpleTerm(
                    value=newsletter.getPath(),
                    token=str(newsletter.getPath()),
                    title=newsletter.getPath()
                )
            )

        return SimpleVocabulary(terms)


NewslettersVocabularyFactory = NewslettersVocabulary()
