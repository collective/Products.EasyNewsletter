from Products.Archetypes import atapi
from Products.CMFCore import utils as cmfutils
from zope.i18nmessageid import MessageFactory
EasyNewsletterMessageFactory = MessageFactory('EasyNewsletter')

# avoid circular import
from Products.EasyNewsletter import config


def initialize(context):
    """Intializer called when used as a Zope 2 product.
    """

    # imports packages and types for registration
    import content

    # initialize portal content
    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    cmfutils.ContentInit(
        config.PROJECTNAME + ' Content',
        content_types = content_types,
        permission = "Add portal content",
        extra_constructors = constructors,
        fti = ftis,
        ).initialize(context)
