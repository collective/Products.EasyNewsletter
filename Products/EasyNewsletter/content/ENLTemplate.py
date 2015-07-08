# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _
from Products.EasyNewsletter import config
from Products.TemplateFields import ZPTField
from plone.dexterity.content import Item
from plone.supermodel import model
from zope.interface import implementer
from zope import schema


class IENLTemplate(model.Schema):
    """ Template used for styling newsletter entries.
    """

    body = schema.Text(
        title=_(u'label_body_zpt', default=u'Newsletter Template'),
        description=_(
            u'help_body_zpt',
            default=u'This is a Zope Page Template file that is used for rendering the newsletter mail.'
        ),
        default=config.DEFAULT_TEMPLATE,
    )

    description = schema.Text(
        title=_(u"label_description", default=u'Description'),
        description=_(
            u"help_description",
            default=u"Enter a value for description."
        ),
    )    


@implementer(IENLTemplate)
class ENLTemplate(Item):
    """ Template used for styling newsletter entries.
    """

    def getSourceCode(self):
        """Return body as string
        """
        html = self.body.getRaw(self)
        return html

    def setIssue(self, issue_uid):
        """Sets the newsletter which should be used by the template
        """
        self.issue_uid = issue_uid

    def queryCatalog(self):
        """Delegates queryCatalog to the current issue.
        """
        portal_catalog = getToolByName(self, "portal_catalog")
        try:
            brain = portal_catalog(UID=self.issue_uid)[0]
            issue = brain.getObject()
            return issue.queryCatalog()
        except (AttributeError, IndexError, TypeError):
            return []

    def getSubTopics(self):
        """
        """
        portal_catalog = getToolByName(self, "portal_catalog")
        try:
            brain = portal_catalog(UID=self.issue_uid)[0]
        except (AttributeError, IndexError):
            return []
        else:
            newsletter = brain.getObject()
            return newsletter.getSubTopics()
