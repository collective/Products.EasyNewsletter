# -*- coding: utf-8 -*-
from Products.Archetypes import atapi
from Products.CMFCore import utils as cmfutils
# avoid circular import
from Products.EasyNewsletter import config  # noqa
from zope.i18nmessageid import MessageFactory


EasyNewsletterMessageFactory = MessageFactory('EasyNewsletter')


def initialize(context):
    """Intializer called when used as a Zope 2 product.
    """

    # initialize portal content
    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    cmfutils.ContentInit(
        config.PROJECTNAME + ' Content',
        content_types=content_types,
        permission="Add portal content",
        extra_constructors=constructors,
        fti=ftis,
    ).initialize(context)
