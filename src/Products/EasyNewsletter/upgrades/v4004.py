# -*- coding: utf-8 -*-

from plone import api

from . import logger


def upgrade(setup_tool=None):
    """ """
    logger.info("Set default aggregation_template on existing Collections")
    brains = api.content.find(portal_type="Collection")
    for brain in brains:
        collection = brain.getObject()
        collection.aggregation_template = "aggregation_generic_listing"
