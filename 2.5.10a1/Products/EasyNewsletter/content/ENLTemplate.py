# python imports
import re

# zope imports
from zope.interface import implements

# Zope / Plone import
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.TemplateFields import ZPTField
from Products.CMFCore.utils import getToolByName

# EasyNewsletter imports
from Products.EasyNewsletter.config import *
from Products.EasyNewsletter.interfaces import IENLTemplate
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _

schema=Schema((
    
    ZPTField('body',
        validators=('zptvalidator',),
        widget=TextAreaWidget(
            description = 'This is a Zope Page Template file '
                    'that is used for rendering the newsletter mail.',
                    description_msgid = "help_body_zpt",
                    label = 'Newsletter Template',
                    label_msgid = "label_body_zpt",
                    i18n_domain = "plone",
                    rows = 30,
                    ) ,
    ),

    TextField('description',
        widget=TextAreaWidget(
            label_msgid="label_description",
            description_msgid="help_description",
            description="Enter a value for description.",
            i18n_domain="plone",
            label='Description',
        ),
        accessor="Description"
    ),

),
)

class ENLTemplate(BaseContent):
    """Template used for styling newsletter entries.
    """
    implements(IENLTemplate)

    security = ClassSecurityInfo()
    schema = BaseSchema + schema

    def initializeArchetype(self, **kwargs):
        """overwritten hook
        """
        BaseContent.initializeArchetype(self, **kwargs)
        self.setBody(DEFAULT_TEMPLATE)

    security.declarePublic('getSourceCode')
    def getSourceCode(self):
        """Return body as string
        """
        html =  self.getField("body").getRaw(self)
        return html

    security.declarePublic('setNewsletter')
    def setIssue(self, issue_uid):
        """Sets the newsletter which should be used by the template
        """
        self.issue_uid = issue_uid

    def queryCatalog(self):
        """Delegates queryCatalog to the current issue.
        """
        portal_catalog = getToolByName(self, "portal_catalog")
        try:
            brain = portal_catalog(UID = self.issue_uid)[0]
            issue = brain.getObject()
            return issue.queryCatalog()
        except (AttributeError, IndexError, TypeError):
            return []

    def getSubTopics(self):
        """
        """
        portal_catalog = getToolByName(self, "portal_catalog")
        try:
            brain = portal_catalog(UID = self.issue_uid)[0]
        except (AttributeError, IndexError):
            return []
        else:
            newsletter = brain.getObject()
            return newsletter.getSubTopics()

registerType(ENLTemplate, PROJECTNAME)
