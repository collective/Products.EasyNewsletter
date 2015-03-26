from plone import api

from logging import getLogger

logger = getLogger('Subscribers')


def fullname_to_first_and_lastname(context):
    """Migrate subscriber fullname to first and lastname fields."""

    catalog = api.portal.get_tool("portal_catalog")
    subscribers = catalog(portal_type='ENLSubscriber')

    for subscriber in subscribers:
        obj = subscriber.getObject()
        names = obj.get('fullname', '').split(' ')
        lastname = names.pop()
        firstname = ' '.join(names)
        import ipdb; ipdb.set_trace()
        if not obj.getLastname():
            obj.setLastname = lastname
        if not obj.getFirstname():
            obj.setFirstname = firstname
        obj.reindexObject()
        logger.info(
            'Splitting fullname to first and lastname for {0}'
            .format(obj.getTitle()))
