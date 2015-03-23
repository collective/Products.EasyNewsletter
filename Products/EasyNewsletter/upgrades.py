from plone import api

from logging import getLogger

logger = getLogger('Subscribers')


def ms_to_mrs(context):
    """Migrate subscriber salutation from ms to mrs."""

    catalog = api.portal.get_tool("portal_catalog")
    subscribers = catalog(portal_type='ENLSubscriber')

    for subscriber in subscribers:
        obj = subscriber.getObject()
        obj_title = obj.getTitle()
        if obj.salutation == 'ms':
            obj.salutation = 'mrs'
            obj.reindexObject()
            logger.info('Updating salutation for ... {0}'.format(obj_title))
