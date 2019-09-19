# -*- coding: utf-8 -*-
from plone.indexer import indexer
from Products.EasyNewsletter.interfaces import IENLSubscriber


@indexer(IENLSubscriber)
def SearchableText(obj):
    user = IENLSubscriber(obj, None)
    if user is None:
        return None
    searchable = ' '.join(filter(None, (obj.getName_prefix(),
                                        obj.getFirstname(),
                                        obj.getLastname(),
                                        obj.getOrganization(),
                                        obj.getEmail())))
    return searchable
