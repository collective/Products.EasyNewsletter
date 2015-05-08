# -*- coding: utf-8 -*-
from logging import getLogger
from nameparser import HumanName
from plone import api


def fullname_to_first_and_lastname(context):
    """Migrate subscriber fullname to separate fields."""

    logger = getLogger('Products.EasyNewsletter.Subscribers')

    catalog = api.portal.get_tool("portal_catalog")
    subscribers = catalog(portal_type='ENLSubscriber')

    for subscriber in subscribers:
        obj = subscriber.getObject()
        fullname = ''
        try:
            fullname = HumanName(obj.fullname)
        except:
            logger.info(
                'No splitting necessary for {0}'.format(obj.getTitle()))
        if fullname:
            if not obj.getLastname():
                obj.setLastname(fullname.last)
            if not obj.getFirstname():
                obj.setFirstname(fullname.first)
            if not obj.getName_prefix():
                obj.setName_prefix(fullname.title)
            obj.reindexObject()
            logger.info(
                'Splitting fullname to first and lastname for {0}'.format(
                    obj.getTitle()
                )
            )


def add_catalog_indexes(context, logger=None):
    """Add aditional indexes to the portal_catalog."""

    logger = getLogger('Products.EasyNewsletter')

    catalog = api.portal.get_tool("portal_catalog")

    indexes = catalog.indexes()
    wanted = (('fullname', 'FieldIndex'),
              ('firstname', 'FieldIndex'),
              ('lastname', 'FieldIndex'),
              ('nl_language', 'FieldIndex'),
              ('email', 'FieldIndex'),
              ('organization', 'FieldIndex'),
              )
    indexables = []
    for name, meta_type in wanted:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            indexables.append(name)
            logger.info("Added %s for field %s.", meta_type, name)
    if len(indexables) > 0:
        logger.info("Indexing new indexes %s.", ', '.join(indexables))
        catalog.manage_reindexIndex(ids=indexables)
