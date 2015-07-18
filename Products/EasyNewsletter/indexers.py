from Products.EasyNewsletter.interfaces import IENLSubscriber
from plone.indexer import indexer


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
