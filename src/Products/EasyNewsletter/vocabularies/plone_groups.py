# -*- coding: utf-8 -*-

from plone import api
from plone.dexterity.interfaces import IDexterityContent
from Products.EasyNewsletter.interfaces import IReceiversGroupFilter
from zope.component import subscribers
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


@implementer(IVocabularyFactory)
class PloneGroups(object):
    """
    """

    def __call__(self, context):

        results = []
        group_properties = dict()
        groups = api.group.get_groups()

        # Fix context if you are using the vocabulary in DataGridField.
        # See https://github.com/collective/collective.z3cform.datagridfield/issues/31:  # NOQA: 501
        if not IDexterityContent.providedBy(context):
            req = getRequest()
            context = req.PARENTS[0]

        for group in groups:
            group_id = group.getId()
            group_properties[group_id] = {
                "title": group.getGroupTitleOrName(),
                "email": group.getProperty("email"),
            }
        results = [(id, property["title"]) for id, property in group_properties.items()]

        # run registered group filter:
        for subscriber in subscribers([self], IReceiversGroupFilter):
            results = subscriber.filter(results)

        # create a list of SimpleTerm items:
        terms = []
        for item in results:
            terms.append(SimpleTerm(value=item[0], token=item[0], title=item[1]))
        # Create a SimpleVocabulary from the terms list and return it:
        return SimpleVocabulary(terms)


PloneGroupsFactory = PloneGroups()
