# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from Products.Archetypes import atapi
from Products.ATContentTypes.content.topic import ATTopic
from Products.ATContentTypes.content.topic import ATTopicSchema
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.EasyNewsletter import config
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _
from Products.EasyNewsletter.interfaces import IEasyNewsletter
from Products.EasyNewsletter.interfaces import IReceiversGroupFilter
from Products.EasyNewsletter.interfaces import IReceiversMemberFilter
from Products.EasyNewsletter.interfaces import ISubscriberSource
from Products.EasyNewsletter.utils.enl import IENLUtils
from Products.MailHost.interfaces import IMailHost
from Products.TemplateFields import ZPTField
from zExceptions import BadRequest
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.component import queryUtility
from zope.component import subscribers
from zope.interface import implementer
from plone.registry.interfaces import IRegistry
from plone.app.blob.field import ImageField
import logging


try:
    from inqbus.plone.fastmemberproperties.interfaces import (
        IFastmemberpropertiesTool)
    has_fmp = True
except Exception:
    has_fmp = False


if config.IS_PLONE_5:
    from Products.Archetypes.atapi import TinyMCEWidget as RichTextWidget
else:
    from Products.Archetypes.atapi import RichWidget as RichTextWidget


log = logging.getLogger("Products.EasyNewsletter")


schema = atapi.Schema((
    # TODO: provide a default value here from portals email_from_address
    atapi.StringField(
        'senderEmail',
        required=True,
        validators=('isEmail', ),
        widget=atapi.StringWidget(
            label=_(
                u"EasyNewsletter_label_senderEmail",
                default=u"Sender email"),
            description=_(
                u"EasyNewsletter_help_senderEmail",
                default=u"Default for the sender address of the newsletters."),
            i18n_domain='EasyNewsletter',
        ),
    ),

    atapi.StringField(
        'senderName',
        widget=atapi.StringWidget(
            label=_(
                u"EasyNewsletter_label_senderName",
                default=u"Sender name"),
            description=_(
                u"EasyNewsletter_help_senderName",
                default=u"Default for the sender name of the newsletters."),
            i18n_domain='EasyNewsletter',
        )
    ),

    atapi.StringField(
        'testEmail',
        required=True,
        validators=('isEmail', ),
        widget=atapi.StringWidget(
            label=_(
                u"EasyNewsletter_label_testEmail",
                default=u"Test email"),
            description=_(
                u"EasyNewsletter_help_testEmail",
                default=u"Default for the test email address."),
            i18n_domain='EasyNewsletter',
        ),
    ),

    atapi.ReferenceField(
        'contentAggregationSources',
        multiValued=1,
        referencesSortable=1,
        relationship='contentAggregationSource',
        allowed_types_method="get_allowed_content_aggregation_types",
        widget=ReferenceBrowserWidget(
            allow_sorting=1,
            label=_(
                u"ENL_content_aggregation_sources_label",
                default=u"Content aggregation sources"),
            description=_(
                u"ENL_content_aggregation_sources_desc",
                default=u"Choose sources to aggregate newsletter content from."
            ),
        ),
    ),

    atapi.LinesField(
        'salutations',
        default=("mr|Dear Mr.", "ms|Dear Ms.", "default|Dear"),
        schemata='personalization',
        widget=atapi.LinesWidget(
            label=_(
                u'EasyNewsletter_label_salutations',
                default=u"Subscriber Salutations."),
            description=_(
                u"EasyNewsletter_help_salutations",
                default=u'Define here possible salutations for subscriber. \
                    One salutation per line in the form of: \"mr|Dear Mr.\". \
                    The left hand value "mr" or "ms" is mapped to salutation \
                    of each subscriber and then the right hand value, which \
                    you can customize is used as salutation.'),
            i18n_domain='EasyNewsletter',
        ),
    ),

    atapi.StringField(
        'fullname_fallback',
        default="Sir or Madam",
        schemata='personalization',
        widget=atapi.StringWidget(
            label=_(
                u'EasyNewsletter_label_fullname_fallback',
                default=u"Fallback for subscribers without a name."),
            description=_(
                u"EasyNewsletter_help_fullname_fallback",
                default=u'This will be used if the subscriber has '
                        'no fullname.'),
            i18n_domain='EasyNewsletter',
        ),
    ),

    atapi.StringField(
        'unsubscribe_string',
        default="Click here to unsubscribe",
        schemata='personalization',
        widget=atapi.StringWidget(
            label=_(
                u"EasyNewsletter_label_unsubscribe_string",
                default=u"Text for the 'unsubscribe' link"),
            description=_(
                u"EasyNewsletter_help_unsubscribe_string",
                default=u'This will replace the placeholder {{UNSUBSCRIBE}}.'),
            i18n_domain='EasyNewsletter',
        ),
    ),

    ImageField(
        'image',
        schemata='personalization',
        max_size=(600, 600),
        widget=atapi.ImageWidget(
            display_threshold=512000,
            label=_(
                u"ENL_image_label",
                default=u"Banner image"),
            description=_(
                u"ENL_image_desc",
                default=u"Banner image, you can include in the templates by" +
                        u"\n adding the {{banner}} placeholder into it."
            ),
        ),
    ),

    ImageField(
        'logo',
        schemata='personalization',
        max_size=(768, 768),
        widget=atapi.ImageWidget(
            display_threshold=512000,
            label=_(
                u"ENL_logo_label",
                default=u"Logo image"),
            description=_(
                u"ENL_logo_desc",
                default=u"Logo image, you can include in the templates by\n"\
                        + u" adding the {{logo}} placeholder into it."
            ),
        ),
    ),

    atapi.TextField(
        'default_header',
        default="{{SUBSCRIBER_SALUTATION}}<br />",
        schemata='personalization',
        allowable_content_types=(
            'text/html', 'text/x-plone-outputfilters-html'),
        default_output_type='text/html',
        widget=RichTextWidget(
            rows=10,
            label=_(
                u"EasyNewsletter_label_default_header",
                default=u"Header"),
            description=_(
                u'description_text_header',
                default=u'The default header text. This is used as a default \
                    for new issues. You can use the placeholders \
                    {{SUBSCRIBER_SALUTATION}} and {{UNSUBSCRIBE}} here.'),
            i18n_domain='EasyNewsletter',
        ),
    ),

    atapi.TextField(
        'default_footer',
        schemata='personalization',
        allowable_content_types=(
            'text/html', 'text/x-plone-outputfilters-html'),
        default="<h1>Community Newsletter for Plone</h1>\n{{UNSUBSCRIBE}}",
        default_output_type='text/html',
        widget=RichTextWidget(
            rows=10,
            label=_(u"EasyNewsletter_label_default_footer", default=u"Footer"),
            description=_(
                u'description_text_footer',
                default=u'The default footer text. This is used as a default \
                    for new issues. You can use the placeholders \
                    {{SUBSCRIBER_SALUTATION}} and {{UNSUBSCRIBE}} here.'),
            i18n_domain='EasyNewsletter',
        ),
    ),

    atapi.BooleanField(
        'excludeAllSubscribers',
        default=False,
        schemata='recipients',
        widget=atapi.BooleanWidget(
            label=_(
                u'label_excludeAllSubscribers',
                default=u'Exclude all subscribers'),
            description=_(
                u'help_excludeAllSubscribers',
                default=u'If checked, the newsletter/mailing will not be send  \
                   to all subscribers inside the newsletter. Changing this \
                   setting does not affect already existing issues.'),
            i18n_domain='EasyNewsletter',
        )
    ),

    atapi.BooleanField(
        'sendToAllPloneMembers',
        default=False,
        schemata='recipients',
        widget=atapi.BooleanWidget(
            label=_(
                u'label_sendToAllPloneMembers',
                default=u'Send to all Plone members'),
            description=_(
                u'help_sendToAllPloneMembers',
                default=u'If checked, the newsletter/mailing is send to all \
                    plone members. If there are subscribers inside the \
                    newsletter, they get the letter anyway. Changing this \
                    setting does not affect already existing issues.'),
            i18n_domain='EasyNewsletter',
        )
    ),

    atapi.LinesField(
        'ploneReceiverMembers',
        vocabulary="get_plone_members",
        schemata='recipients',
        widget=atapi.MultiSelectionWidget(
            label=_(
                u"EasyNewsletter_label_ploneReceiverMembers",
                default=u"Plone Members to receive the newsletter"),
            description=_(
                u"EasyNewsletter_help_ploneReceiverMembers",
                default=u"Choose Plone Members which should receive \
                    the newsletter. Changing this setting does not affect \
                    already existing issues."),
            i18n_domain='EasyNewsletter',
            size=20,
        )
    ),

    atapi.LinesField(
        'ploneReceiverGroups',
        vocabulary="get_plone_groups",
        schemata='recipients',
        widget=atapi.MultiSelectionWidget(
            label=_(
                u"EasyNewsletter_label_ploneReceiverGroups",
                default=u"Plone Groups to receive the newsletter"),
            description=_(
                u"EasyNewsletter_help_ploneReceiverGroups",
                default=u"Choose Plone Groups which members should \
                    receive the newsletter. Changing this setting does not \
                    affect already existing issues."),
            i18n_domain='EasyNewsletter',
            size=10,
        )
    ),

    atapi.StringField(
        'subscriberSource',
        schemata='settings',
        vocabulary="get_subscriber_sources",
        default='default',
        widget=atapi.SelectionWidget(
            label=_(
                u"EasyNewsletter_label_externalSubscriberSource",
                default="External subscriber source"),
            description=_(
                u"EasyNewsletter_help_externalSubscriberSource",
                default=u"Some packages provide an external subscriber source \
                    for EasyNewsletter. If one is installed you can \
                    choose it here."),
            i18n_domain='EasyNewsletter',
            size=10,
        )
    ),

    atapi.StringField(
        'deliveryService',
        schemata='settings',
        vocabulary="get_delivery_services",
        default='mailhost',
        widget=atapi.SelectionWidget(
            label=_(
                u"EasyNewsletter_label_externalDeliveryService",
                default=u"External delivery service"),
            description=_(
                u"EasyNewsletter_help_externalDeliveryService",
                default=u"Some packages provide an external delivery service \
                    for EasyNewsletter. If one is installed you can choose \
                    it here."),
            i18n_domain='EasyNewsletter',
            size=10,
        )
    ),

    # XXX can be removed in version 4
    ZPTField(
        'out_template_pt',
        schemata='settings',
        required=False,
        validators=('zptvalidator', ),
        widget=atapi.TextAreaWidget(
            label=_(
                u"label_out_template_pt",
                default=u"Outgoing Mail Template, NOT USED ANY MORE!"),
            description=_(
                u"help_mailtemplate_body_pt",
                default=u"This is not used anymore and will be removed in \
                    future, please see docs for output templates."),
            i18n_domain="EasyNewsletter",
            rows=40,
        ),
    ),

    atapi.StringField(
        'outputTemplate',
        vocabulary="get_output_templates",
        required=True,
        default_method='get_default_output_template',
        widget=atapi.SelectionWidget(
            label=_(
                u"enl_label_output_template",
                default="Output template"),
            description=_(
                u"enl_help_output_template",
                default=u"Choose the template to render the email. "
            ),
            i18n_domain='EasyNewsletter',
            size=1,
        )
    ),

    atapi.StringField(
        'template',
        schemata='settings',
        default_method='get_default_aggregation_template',
        required=0,
        widget=atapi.StringWidget(
            macro='NewsletterTemplateWidget',
            label=_(
                u'EasyNewsletter_label_template',
                default=u'Content Aggregation Template'),
            description=_(
                u'EasyNewsletter_help_template',
                default=u'Template to used to render aggregated content.'),
            i18n_domain='EasyNewsletter',
        ),
    ),

    # XXX move these settings into the plone registry,
    # so we can easy customize them
    atapi.StringField(
        'subscriber_confirmation_mail_subject',
        schemata="settings",
        required=True,
        default=config.DEFAULT_SUBSCRIBER_CONFIRMATION_MAIL_SUBJECT,
        widget=atapi.StringWidget(
            label=_(
                u'EasyNewsletter_label_subscriber_confirmation_mail_subject',
                default=u'Subscriber confirmation mail subject'),
            description=_(
                u'EasyNewsletter_description_subscriber_confirmation'
                u'_mail_subject',
                default=u'Text used for confirmation email subject. You can \
                    customize the text, but it should include the \
                    placeholder: ${portal_url}!'),
            i18n_domain='EasyNewsletter',
        ),
    ),

    # XXX move these settings into the plone registry,
    # so we can easy customize them
    atapi.TextField(
        'subscriber_confirmation_mail_text',
        schemata="settings",
        required=True,
        default=config.DEFAULT_SUBSCRIBER_CONFIRMATION_MAIL_TEXT,
        widget=atapi.TextAreaWidget(
            rows=8,
            label=_(
                u'EasyNewsletter_label_subscriber_confirmation_mail_text',
                default=u'Subscriber confirmation mail text'),
            description=_(
                u'description_subscriber_confirmation_mail_text',
                default=u'Text used for confirmation email. You can customize \
                    the text, but it should include the placeholders: \
                    ${portal_url}, ${subscriber_email} and \
                    ${confirmation_url}!'),
            i18n_domain='EasyNewsletter',
        ),
    ),
),
)


schema = ATTopicSchema.copy() + schema
schema['text'].widget.description = _(
    u'description_text',
    default=u'This is used in the frontpage of EasyNewsletter \
            on top of Issue archive list.')

schema['limitNumber'].widget.visible = {
    'view': 'invisible', 'edit': 'invisible'}
schema['itemCount'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['customView'].widget.visible = {
    'view': 'invisible', 'edit': 'invisible'}
schema['customViewFields'].widget.visible = {
    'view': 'invisible', 'edit': 'invisible'}
schema['allowDiscussion'].widget.visible = {
    'view': 'invisible', 'edit': 'invisible'}
schema['subject'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['location'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['effectiveDate'].widget.visible = {
    'view': 'invisible', 'edit': 'invisible'}
schema['expirationDate'].widget.visible = {
    'view': 'invisible', 'edit': 'invisible'}
schema['creators'].widget.visible = {
    'view': 'invisible', 'edit': 'invisible'}
schema['contributors'].widget.visible = {
    'view': 'invisible', 'edit': 'invisible'}
schema['rights'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}

schema['relatedItems'].schemata = "settings"
schema['language'].schemata = "settings"
schema['excludeFromNav'].schemata = "settings"
schema.moveField('contentAggregationSources', after='title')
schema.moveField('testEmail', after='title')
schema.moveField('senderName', after='title')
schema.moveField('senderEmail', after='title')
schema.moveField('deliveryService', pos='bottom')
schema.moveField('subscriberSource', pos='bottom')
schema.moveField('relatedItems', pos='bottom')
schema.moveField('language', pos='bottom')
schema.moveField('excludeFromNav', pos='bottom')

schema.moveField('default_footer', after='contentAggregationSources')
schema.moveField('default_header', after='contentAggregationSources')
schema.moveField('unsubscribe_string', after='contentAggregationSources')
schema.moveField('fullname_fallback', after='contentAggregationSources')
schema.moveField('salutations', after='contentAggregationSources')

schema.moveField('excludeAllSubscribers', after='default_footer')


@implementer(IEasyNewsletter)
class EasyNewsletter(ATTopic, atapi.BaseFolder):
    """A folder for managing and archiving newsletters.
    """
    security = ClassSecurityInfo()
    schema = schema
    _at_rename_after_creation = True

    def get_allowed_content_aggregation_types(self):
        enl_utils = getUtility(IENLUtils)
        return enl_utils.get_allowed_content_aggregation_types()

    def get_default_aggregation_template(self):
        """ return the default template key """
        registry = getUtility(IRegistry)
        templates_keys = registry.get(
            'Products.EasyNewsletter.content_aggregation_templates').keys()
        if templates_keys:
            if 'aggregation_news_events_listing' in templates_keys:
                default_tmpl_key = 'aggregation_news_events_listing'
            else:
                default_tmpl_key = templates_keys[0]
        else:
            default_tmpl_key = 'custom'
        return default_tmpl_key

    def get_aggregation_template_objects(self):
        enl = self
        return enl.objectValues('ENLTemplate')

    def get_output_templates(self):
        """ Return registered output templates as DisplayList """
        result = atapi.DisplayList()
        registry = getUtility(IRegistry)
        output_templates = registry.get(
            'Products.EasyNewsletter.output_templates')
        if not output_templates:
            return result
        for key, value in output_templates.items():
            result.add(key, value)
        if not len(result):
            result.add(u'output_default', _(
                u'enl_label_default_output_template',
                u'Default output template'))
        return result

    def get_default_output_template(self):
        registry = getUtility(IRegistry)
        templates_keys = registry.get(
            'Products.EasyNewsletter.output_templates').keys()
        if not templates_keys:
            return
        if 'output_default' in templates_keys:
            default_tmpl_key = 'output_default'
        else:
            default_tmpl_key = templates_keys[0]
        return default_tmpl_key

    @security.public
    def initializeArchetype(self, **kwargs):
        """Overwritten hook.
        """
        ATTopic.initializeArchetype(self, **kwargs)

        def create_template(id="", title=""):
            """ Add template object """
            if getattr(self.aq_explicit, id, None):
                log.info("ENLTemplate obj already exists: %s" % id)
                return
            self.manage_addProduct["EasyNewsletter"].addENLTemplate(
                id=id, title=title)
            self[id].setAggregationTemplate(id)

        registry = getUtility(IRegistry)
        aggregation_templates = registry.get(
            'Products.EasyNewsletter.content_aggregation_templates')
        if not aggregation_templates:
            log.warn(
                "No aggregation_templates found, ",
                "skip creating ENLTemplate objs!")
            return
        for key, value in aggregation_templates.items():
            tmpl_id = str(key)
            create_template(id=tmpl_id, title=value)

    # XXX factore this out for DX reimplementation
    @security.public
    def addSubscriber(self, subscriber, firstname, lastname, name_prefix,
                      nl_language, organization, salutation=None):
        """Adds a new subscriber to the newsletter (if valid).
        """
        # we need the subscriber email here as an id,
        # to check for existing entries
        email = subscriber
        plone_utils = getToolByName(self, 'plone_utils')
        subscriber_id = plone_utils.normalizeString(email)
        portal = getToolByName(self, 'portal_url').getPortalObject()
        try:
            execute_under_special_role(
                portal, "Contributor", self.invokeFactory, "ENLSubscriber",
                id=subscriber_id, language=self.Language())
        except BadRequest:
            return (False, "email_exists")
        o = getattr(self, subscriber_id)
        o.setEmail(subscriber)
        o.setFirstname(firstname)
        o.setLastname(lastname)
        o.setName_prefix(name_prefix)
        o.setNl_language(nl_language)
        o.setOrganization(organization)
        o.setSalutation(salutation)
        o.reindexObject()

        return (True, "subscription_confirmed")

    def _get_fmp_tool(self):
        if has_fmp:
            log.debug("Use fastmemberpropertiestool to get memberproperties!")
            fmp_tool = queryUtility(
                IFastmemberpropertiesTool,
                'fastmemberproperties_tool'
            )
            if fmp_tool is None:
                log.warn(
                    'inqbus.plone.fastmemberproperties installed but cant '
                    'get tool, check the configuration.'
                )
            return fmp_tool
        return False

    def get_plone_members(self):
        """ return filtered list of plone members as DisplayList
        """
        fmp_tool = self._get_fmp_tool()
        if fmp_tool:
            member_properties = fmp_tool.get_all_memberproperties()
        else:
            log.info(
                'Currently plone API is used to get memberproperties, '
                'this is very slow on many members, please consider '
                'installing inqbus.plone.fastmemberproperties to make it fast!'
            )
            acl_userfolder = getToolByName(self, 'acl_users')
            member_objs = acl_userfolder.getUsers()
            member_properties = {}
            for member in member_objs:
                probdict = {}
                probdict['id'] = member.getUserId()
                probdict['email'] = member.getProperty('email')
                probdict['fullname'] = safe_unicode(
                    member.getProperty('fullname'))
                member_properties[probdict['id']] = probdict
        if not member_properties:
            return []

        results = []
        try:
            for id, property in member_properties.items():
                if config.EMAIL_RE.findall(property['email']):
                    results.append(
                        (id, property['fullname'] + ' - ' + property['email']))
                else:
                    log.error(
                        "Property email: \"%s\" is not an email!" %
                        property['email'])
        except TypeError, e:  # noqa
            log.error(":get_plone_members: error in member_properties %s \
                properties:'%s'" % (e, member_properties.items()))
        # run registered member filter:
        for subscriber in subscribers([self], IReceiversMemberFilter):
            results = subscriber.filter(results)

        results = atapi.DisplayList(results)
        return results.sortedByValue()

    def get_plone_groups(self):
        """ return filtered list of plone groups as DisplayList
        """
        gtool = getToolByName(self, 'portal_groups')
        groups = gtool.listGroups()
        group_properties = {}
        for group in groups:
            group_id = group.getId()
            group_properties[group_id] = {
                'title': group.getGroupTitleOrName(),
                'email': group.getProperty('email'),
            }
        results = [
            (id, property['title'])
            for id, property in group_properties.items()]
        # run registered group filter:
        for subscriber in subscribers([self], IReceiversGroupFilter):
            results = subscriber.filter(results)
        results = atapi.DisplayList(results)
        return results.sortedByValue()

    def getNewsletter(self):
        """ return the (parent) Newsletter instance using Acquisition """
        return self

    def get_subscriber_sources(self):
        result = atapi.DisplayList()
        result.add(u'default', _(
            u'EasyNewsletter_label_noSource',
            u'no external subscriber source'))
        for utility in getUtilitiesFor(ISubscriberSource):
            result.add(utility[0], utility[0])
        return result

    def get_delivery_services(self):
        result = atapi.DisplayList()
        result.add(u'mailhost', _(
            u'EasyNewsletter_label_PloneMailHost', u'Default Plone Mailhost'))
        for utility in getUtilitiesFor(IMailHost):
            if utility[0]:
                result.add(utility[0], utility[0])
        return result

    def get_send_issues(self):
        """ return sended issues brains"""
        enl = self.getNewsletter()
        issues = self.portal_catalog(
            portal_type=config.ENL_ISSUE_TYPES,
            review_state='sent',
            sort_on='modified',
            sort_order='reverse',
            path='/'.join(enl.getPhysicalPath())
        )
        return issues

    def get_draft_issues(self):
        """ return draft issues brains"""
        enl = self.getNewsletter()
        issues = self.portal_catalog(
            portal_type=config.ENL_ISSUE_TYPES,
            review_state=['draft', 'sending'],
            sort_on='modified',
            sort_order='reverse',
            path='/'.join(enl.getPhysicalPath())
        )
        return issues

    def get_master_issues(self):
        """ return issues brains of issues in review state master"""
        enl = self.getNewsletter()
        issues = self.portal_catalog(
            portal_type=config.ENL_ISSUE_TYPES,
            review_state='master',
            sort_on='modified',
            sort_order='reverse',
            path='/'.join(enl.getPhysicalPath())
        )
        return issues


atapi.registerType(EasyNewsletter, config.PROJECTNAME)


class UnrestrictedUser(BaseUnrestrictedUser):
    """Unrestricted user that still has an id.
    """

    def getId(self):
        """Return the ID of the user.
        """
        return self.getUserName()


def execute_under_special_role(portal, role, function, *args, **kwargs):
    """ Execute code under special role priviledges.
    Example how to call::
        execute_under_special_role(portal, "Manager",
            doSomeNormallyNotAllowedStuff,
            source_folder, target_folder)

    @param portal: Reference to ISiteRoot obj whose access ctls we are using
    @param function: Method to be called with special priviledges
    @param role: User role we are using for the security context when calling \
                 the priviledged code. For example, use "Manager".
    @param args: Passed to the function
    @param kwargs: Passed to the function
    """

    sm = getSecurityManager()
    try:
        try:
            # Clone the current access control user and assign a new role
            # for him/her. Note that the username (getId()) is left in
            # exception tracebacks in error_log
            # so it is important thing to store
            tmp_user = UnrestrictedUser(
                sm.getUser().getId(), '', [role], '')

            # Act as user of the portal
            tmp_user = tmp_user.__of__(portal.acl_users)
            newSecurityManager(None, tmp_user)

            # Call the function
            return function(*args, **kwargs)

        except Exception:
            # If special exception handlers are needed, run them here
            raise
    finally:
        # Restore the old security manager
        setSecurityManager(sm)
