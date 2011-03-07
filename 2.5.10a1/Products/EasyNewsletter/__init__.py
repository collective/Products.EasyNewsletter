# CMFCore imports
from Products.CMFCore import utils as cmfutils
from Products.CMFCore import DirectoryView

# Archetypes imports
from Products.Archetypes.atapi import *
from Products.Archetypes import listTypes

from zope.i18nmessageid import MessageFactory
EasyNewsletterMessageFactory = MessageFactory('EasyNewsletter')

from Products.EasyNewsletter.config import *
        
def initialize(context):
    """Intializer called when used as a Zope 2 product.
    """

    # imports packages and types for registration
    import content
    
    # initialize portal content
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = "Add portal content",
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)
