# -*- coding: utf-8 -*-
from plone import api
from Products.EasyNewsletter.content.newsletter import INewsletter
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


@implementer(IVocabularyFactory)
class NewslettersVocabulary(object):
    """Provide available newsletters."""

    def __call__(self, context):
        terms = []
        newsletters = api.content.find(object_provides=INewsletter)
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
