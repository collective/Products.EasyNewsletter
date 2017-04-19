# -*- coding: utf-8 -*-
from Acquisition import aq_inner, aq_parent
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _  # noqa
from Products.EasyNewsletter import config
from Products.EasyNewsletter.interfaces import IENLTemplate
from Products.TemplateFields import ZPTField
from zope.interface import implementer
from zope.site.hooks import getSite


schema = atapi.BaseSchema + atapi.Schema((
    # XXX provide a default_method to select template from registry if possible
    # this could be combined with an email render behavior on the content
    # source target objects like Collection.
    ZPTField(
        'body',
        validators=('zptvalidator', ),
        widget=atapi.TextAreaWidget(
            label=_(u'label_body_zpt', default=u'Newsletter Template'),
            description=_(
                'help_body_zpt',
                default=u'This is a Zope Page Template file that is used for \
                     rendering the newsletter mail.'),
            i18n_domain="plone",
            rows=90,
        ),
    ),

    atapi.TextField(
        'description',
        accessor="Description",
        widget=atapi.TextAreaWidget(
            label=_(u"label_description", default=u'Description'),
            description=_(
                u"help_description",
                default=u"Enter a value for description."),
            i18n_domain="plone",
        ),
    ),

), )


@implementer(IENLTemplate)
class ENLTemplate(atapi.BaseContent):
    """Template used for styling newsletter entries.
    """
    security = ClassSecurityInfo()
    schema = schema
    _at_rename_after_creation = True

    def initializeArchetype(self, **kwargs):  # noqa
        """overwritten hook
        """
        atapi.BaseContent.initializeArchetype(self, **kwargs)
        portal = getSite()
        template_obj = portal.restrictedTraverse(
            'email_templates/aggregation_news_events_listing')
        self.setBody(template_obj.read())

    @security.public
    def getSourceCode(self):  # noqa
        """Return body as string
        """
        html = self.getField("body").getRaw(self)
        return html

    @security.public
    def setIssue(self, issue_uid):  # noqa
        """Sets the newsletter which should be used by the template
        """
        self.issue_uid = issue_uid

    def getContentSources(self):  # noqa
        """
        """
        portal_catalog = getToolByName(self, "portal_catalog")
        try:
            brain = portal_catalog(UID=self.issue_uid)[0]
        except (AttributeError, IndexError):
            return []
        else:
            issue = brain.getObject()
            content_sources = issue.getContentAggregationSources()
            if not content_sources:
                content_sources = aq_parent(aq_inner(
                    issue)).getContentAggregationSources()
            if not content_sources:
                return []
            return content_sources


atapi.registerType(ENLTemplate, config.PROJECTNAME)
