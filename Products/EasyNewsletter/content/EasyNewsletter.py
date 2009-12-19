# python imports
import re

# zope imports
from zope.interface import implements
 
# Zope / Plone imports
from zExceptions import BadRequest
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes import ATCTMessageFactory as _
from Products.ATContentTypes.content.topic import ATTopic
from Products.ATContentTypes.content.topic import ATTopicSchema

# EasyNewsletter imports
from Products.EasyNewsletter.interfaces import IEasyNewsletter
from Products.EasyNewsletter.config import PROJECTNAME

schema=Schema((
    StringField('senderEmail',
        widget=StringWidget(
            label="Sender e-mail",
            description="Default for the sender address of the newsletters.",
            label_msgid='EasyNewsletter_label_senderEmail',
            description_msgid='EasyNewsletter_help_senderEmail',
            i18n_domain='EasyNewsletter',
        ),
        required=True,
        validators=('isEmail',)
    ),

    StringField('senderName',
        widget=StringWidget(
            label="Sender name",
            description="Default for the sender name of the newsletters.",
            label_msgid='EasyNewsletter_label_senderName',
            description_msgid='EasyNewsletter_help_senderName',
            i18n_domain='EasyNewsletter',
        )
    ),

    StringField('testEmail',
        widget=StringWidget(
            label="Test e-mail",
            description="Default for the test e-mail address.",
            label_msgid='EasyNewsletter_label_testEmail',
            description_msgid='EasyNewsletter_help_testEmail',
            i18n_domain='EasyNewsletter',
        ),
        required=True,
        validators=('isEmail',)
    ),

    #Overwritten to hide attribute from ATTopic
    BooleanField('limitNumber',
        widget=BooleanWidget(
            visible={'edit':'hidden', 'view':'hidden'},
            label='Limitnumber',
            label_msgid='EasyNewsletter_label_limitNumber',
            description_msgid='EasyNewsletter_help_limitNumber',
            i18n_domain='EasyNewsletter',
        )
    ),

    #Overwritten to hide attribute from ATTopic
    BooleanField('itemCount',
        widget=BooleanWidget(
            visible={'edit':'hidden', 'view':'hidden'},
            label='Itemcount',
            label_msgid='EasyNewsletter_label_itemCount',
            description_msgid='EasyNewsletter_help_itemCount',
            i18n_domain='EasyNewsletter',
        )
    ),

    #Overwritten to hide attribute from ATTopic
    BooleanField('customView',
        widget=BooleanWidget(
            visible={'edit':'hidden', 'view':'hidden'},
            label='Customview',
            label_msgid='EasyNewsletter_label_customView',
            description_msgid='EasyNewsletter_help_customView',
            i18n_domain='EasyNewsletter',
        )
    ),

    #Overwritten to hide attribute from ATTopic
    BooleanField('customViewFields',
        widget=BooleanWidget(
            visible={'edit':'hidden', 'view':'hidden'},
            label='Customviewfields',
            label_msgid='EasyNewsletter_label_customViewFields',
            description_msgid='EasyNewsletter_help_customViewFields',
            i18n_domain='EasyNewsletter',
        )
    ),
),
)

class EasyNewsletter(ATTopic, BaseFolder):
    """A folder for managing and archiving newsletters.
    """
    implements(IEasyNewsletter) 
    security = ClassSecurityInfo()
    schema = ATTopicSchema + schema
    _at_rename_after_creation  = True

    security.declarePublic("initializeArchetype")
    def initializeArchetype(self, **kwargs):
        """Overwritten hook.
        """
        ATTopic.initializeArchetype(self, **kwargs)
        
        # Add default template
        self.manage_addProduct["EasyNewsletter"].addENLTemplate(id="default", title="Default")
        tmpl = self.default

    security.declarePublic("displayContentsTab")
    def displayContentsTab(self):
        """Overwritten to hide contents tab.
        """
        return False

    security.declarePublic('addSubscriber')
    def addSubscriber(self, subscriber):
        """Adds a new subscriber to the newsletter (if valid).
        """
        from Products.validation.validators.BaseValidators import EMAIL_RE
        EMAIL_RE = "^" + EMAIL_RE
        mo = re.search(EMAIL_RE, subscriber)
                
        if mo is None:
            return (False, 1)
        else:
            # Normalize Subscriber
            plone_tool = getToolByName(self, 'plone_utils')    
            subscriber_id = plone_tool.normalizeString(subscriber)
            
            try:
                self.manage_addProduct["EasyNewsletter"].addENLSubscriber(id=subscriber_id)
            except BadRequest:
                return (False, 2)
                
            o = getattr(self, subscriber_id)
            o.setEmail( subscriber)
        
            return (True, 0)
    
    def getSubTopics(self):
        """Returns sub topics.
        """
        return self.objectValues("ATTopic")

registerType(EasyNewsletter, PROJECTNAME)
