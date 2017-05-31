# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from plone.registry.interfaces import IRegistry
from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName
from Products.EasyNewsletter import config
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _  # noqa
from Products.EasyNewsletter.interfaces import IENLTemplate
from Products.TemplateFields import ZPTField
from zope.component import getUtility
from zope.interface import implementer
from zope.site.hooks import getSite


schema = atapi.BaseSchema + atapi.Schema((
    atapi.StringField(
        'aggregationTemplate',
        vocabulary="get_aggregation_templates",
        required=True,
        default_method='get_default_aggregation_template',
        widget=atapi.SelectionWidget(
            label=_(
                u"enl_label_aggregation_template",
                default="Aggregation template"),
            description=_(
                u"enl_help_aggregation_template",
                default=u"Choose the template to render aggregated content. " +
                        u"Changing this from custom to something else, might" +
                        u" override the custom " +
                        u"aggregation template in the field below!"
            ),
            i18n_domain='EasyNewsletter',
            size=1,
        )
    ),

    ZPTField(
        'body',
        validators=('zptvalidator', ),
        widget=atapi.TextAreaWidget(
            label=_(u'label_body_zpt', default=u'Custom Aggregation Template'),
            description=_(
                'help_body_zpt',
                # XXX update translations for this string!
                default=u'This is a custom Zope Page Template that ' +
                        u'is used for rendering the aggregated email content' +
                        u', in case you selected <i>custom</i> for the ' +
                        u'aggregation template above.'),
            i18n_domain="plone",
            rows=90,
        ),
    ),

), )


# schema['body'].widget.visible = {
#    'view': 'invisible', 'edit': 'hidden'}


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
        enl_template_id = self.getAggregationTemplate()
        template_file = portal.restrictedTraverse(enl_template_id)
        self.setBody(template_file.read())

    def get_aggregation_templates(self):
        """ Return registered aggregation templates as DisplayList """
        result = atapi.DisplayList()
        registry = getUtility(IRegistry)
        aggregation_templates = registry.get(
            'Products.EasyNewsletter.content_aggregation_templates')
        for key, value in aggregation_templates.items():
            result.add(key, value)
        result.add(u'custom', _(
            u'enl_label_custom_template',
            u'Custom template field'))
        return result

    def get_default_aggregation_template(self):
        """ return the default template key """
        registry = getUtility(IRegistry)
        templates_keys = registry.get(
            'Products.EasyNewsletter.content_aggregation_templates').keys()
        if templates_keys:
            default_tmpl_key = templates_keys[0]
        else:
            default_tmpl_key = 'custom'
        return default_tmpl_key

    @security.public
    def getSourceCode(self):  # noqa
        """Return body as string
        """
        html = self.getField("body").getRaw(self)
        return html

    # XXX this looks not right, why is this public?
    @security.public
    def setIssue(self, issue_uid):  # noqa
        """Sets the newsletter which should be used by the template
        """
        self.issue_uid = issue_uid

    def getContentSources(self):  # noqa
        """
        """
        portal_catalog = getToolByName(self, "portal_catalog")
        content_sources = None
        issue_uid = getattr(self, 'issue_uid', None)
        if issue_uid:
            try:
                brain = portal_catalog(UID=issue_uid)[0]
            except (AttributeError, IndexError):
                return []
            else:
                if brain:
                    issue = brain.getObject()
                    content_sources = issue.getContentAggregationSources()
        if not content_sources:
            enl = self.getNewsletter()
            content_sources = enl.getContentAggregationSources()
        if not content_sources:
            return []
        return content_sources


atapi.registerType(ENLTemplate, config.PROJECTNAME)
