# zope imports
from zope.interface import implements

# Zope / Plone import
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *

# EasyNewsletter imports
from Products.EasyNewsletter.interfaces import IENLSubscriber
from Products.EasyNewsletter.config import *

schema=Schema((
    StringField('title',
        widget=StringWidget(
            visible={'edit':'invisible', 'view':'invisible'},
            label='Title',
            label_msgid='EasyNewsletter_label_title',
            description_msgid='EasyNewsletter_help_title',
            i18n_domain='EasyNewsletter',
        ),
        required = False
    ),

    StringField('email',
        widget=StringWidget(
            label='Email',
            label_msgid='EasyNewsletter_label_email',
            description_msgid='EasyNewsletter_help_email',
            i18n_domain='EasyNewsletter',
        ),
        validators=('isEmail',)
    ),

),
)

class ENLSubscriber(BaseContent):
    """An newsletter subscriber.
    """
    implements(IENLSubscriber)
    security = ClassSecurityInfo()
    _at_rename_after_creation  = True
    schema = BaseSchema + schema

    def setEmail(self, value):
        """
        """
        self.email = value
        self.title = value

        # reindex to set title for catalog
        self.reindexObject()

    def Title(self):
        """Overwritten accessor for Title
        """
        return self.getEmail()

registerType(ENLSubscriber, PROJECTNAME)