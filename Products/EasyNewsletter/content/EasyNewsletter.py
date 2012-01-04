from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser

from Products.Archetypes import atapi
from Products.ATContentTypes.content.topic import ATTopic
from Products.ATContentTypes.content.topic import ATTopicSchema
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.MailHost.interfaces import IMailHost
from Products.TemplateFields import ZPTField

from zExceptions import BadRequest
from zope.component import queryUtility
from zope.component import getUtilitiesFor
from zope.component import subscribers
from zope.interface import implements

try:
    from inqbus.plone.fastmemberproperties.interfaces import IFastmemberpropertiesTool
    fmp_tool = True
except:
    fmp_tool = False

# EasyNewsletter imports
from Products.EasyNewsletter.interfaces import IReceiversMemberFilter, IReceiversGroupFilter
from Products.EasyNewsletter.interfaces import IEasyNewsletter
from Products.EasyNewsletter.interfaces import ISubscriberSource
from Products.EasyNewsletter import config
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _

import logging
log = logging.getLogger("Products.EasyNewsletter")


schema = atapi.Schema((
    atapi.StringField('senderEmail',
        required = True,
        validators = ('isEmail', ),
        widget = atapi.StringWidget(
            label = _(u"EasyNewsletter_label_senderEmail",
                default=u"Sender email"),
            description = _(u"EasyNewsletter_help_senderEmail",
                default=u"Default for the sender address of the newsletters."),
            i18n_domain = 'EasyNewsletter',
        ),
    ),

    atapi.StringField('senderName',
        widget = atapi.StringWidget(
            label = _(u"EasyNewsletter_label_senderName",
                default=u"Sender name"),
            description = _(u"EasyNewsletter_help_senderName",
                default=u"Default for the sender name of the newsletters."),
            i18n_domain = 'EasyNewsletter',
        )
    ),

    atapi.StringField('testEmail',
        required = True,
        validators = ('isEmail', ),
        widget = atapi.StringWidget(
            label = _(u"EasyNewsletter_label_testEmail",
                default=u"Test email"),
            description = _(u"EasyNewsletter_help_testEmail",
                default=u"Default for the test email address."),
            i18n_domain='EasyNewsletter',
        ),
    ),

    atapi.LinesField('salutations',
        default = ("mr|Dear Mr.", "ms|Dear Ms.", "default|Dear"),
        widget = atapi.LinesWidget(
            label = _(u'EasyNewsletter_label_salutations',
                default=u"Subscriber Salutations."),
            description = _(u"EasyNewsletter_help_salutations",
                default=u'Define here possible salutations for subscriber. One \
                    salutation per line in the form of: \"mr|Dear Mr.\". \
                    The left hand value "mr" or "ms" is mapped to salutation of \
                    each subscriber and then the right hand value, which you \
                    can customize is used as salutation.'),
            i18n_domain = 'EasyNewsletter',
        ),
    ),

    atapi.StringField('fullname_fallback',
        default = "Sir or Madam",
        widget = atapi.StringWidget(
            label = _(u'EasyNewsletter_label_fullname_fallback',
                default=u"Fallback for subscribers without a name."),
            description = _(u"EasyNewsletter_help_fullname_fallback",
                default=u'This will be used if the subscriber has no fullname.'),
            i18n_domain = 'EasyNewsletter',
        ),
    ),

    atapi.StringField('unsubscribe_string',
        default = "Click here to unsubscribe",
        widget = atapi.StringWidget(
            label = _(u"EasyNewsletter_label_unsubscribe_string",
                default=u"Text for the 'unsubscribe' link"),
            description = _(u"EasyNewsletter_help_unsubscribe_string",
                default=u'This will replace the placeholder [[UNSUBSCRIBE]].'),
            i18n_domain = 'EasyNewsletter',
        ),
    ),

    atapi.TextField('default_header',
        default = "[[SUBSCRIBER_SALUTATION]]<br />==================================",
        allowable_content_types = ('text/plain', 'text/structured', 'text/html', 'application/msword'),
        default_output_type='text/html',
        widget = atapi.RichWidget(
            rows = 10,
            label = _(u"EasyNewsletter_label_default_header",
                default=u"Header"),
            description = _(u'description_text_header',
                default=u'The default header text. This is used as a default \
                    for new issues. You can use the placeholders [[SUBSCRIBER_SALUTATION]] and [[UNSUBSCRIBE]] here.'),
            i18n_domain = 'EasyNewsletter',
        ),
    ),

    atapi.TextField('default_footer',
        allowable_content_types = ('text/plain', 'text/structured', 'text/html', 'application/msword'),
        default = "==================================<br />[[UNSUBSCRIBE]]",
        default_output_type = 'text/html',
        widget = atapi.RichWidget(
            rows = 10,
            label = _(u"EasyNewsletter_label_default_footer", default=u"Footer"),
            description = _(u'description_text_footer',
                default=u'The default footer text. This is used as a default \
                    for new issues. You can use the placeholders \
                    [[SUBSCRIBER_SALUTATION]] and [[UNSUBSCRIBE]] here.'),
            i18n_domain = 'EasyNewsletter',
        ),
    ),

    atapi.BooleanField('sendToAllPloneMembers',
        default = False,
        widget = atapi.BooleanWidget(
            label = _(u'label_sendToAllPloneMembers',
                default=u'Send to all Plone members'),
            description = _(u'help_sendToAllPloneMembers',
                default=u'If checked, the newsletter/mailing is send to all \
                    plone members. If there are subscribers inside the \
                    newsletter, they get the letter anyway.'),
            i18n_domain = 'EasyNewsletter',
        )
    ),

    atapi.LinesField('ploneReceiverMembers',
        vocabulary = "get_plone_members",
        widget = atapi.MultiSelectionWidget(
            label = _(u"EasyNewsletter_label_ploneReceiverMembers",
                default=u"Plone Members to receive the newsletter"),
            description = _(u"EasyNewsletter_help_ploneReceiverMembers",
                default=u"Choose Plone Members which should receive the newsletter."),
            i18n_domain = 'EasyNewsletter',
            size = 20,
        )
    ),

    atapi.LinesField('ploneReceiverGroups',
        vocabulary = "get_plone_groups",
        widget = atapi.MultiSelectionWidget(
            label = _(u"EasyNewsletter_label_ploneReceiverGroups",
                default=u"Plone Groups to receive the newsletter"),
            description = _(u"EasyNewsletter_help_ploneReceiverGroups",
                default=u"Choose Plone Groups which members should receive the newsletter."),
            i18n_domain = 'EasyNewsletter',
            size = 10,
        )
    ),

    atapi.StringField('subscriberSource',
        schemata = 'settings',
        vocabulary = "get_subscriber_sources",
        default = 'default',
        widget = atapi.SelectionWidget(
            label = _(u"EasyNewsletter_label_externalSubscriberSource",
                default="External subscriber source"),
            description = _(u"EasyNewsletter_help_externalSubscriberSource",
                default=u"Some packages provide an external subscriber source \
                    for EasyNewsletter. If one is installed you can choose it here."),
            i18n_domain = 'EasyNewsletter',
            size = 10,
        )
    ),

    atapi.StringField('deliveryService',
        schemata = 'settings',
        vocabulary = "get_delivery_services",
        default = 'mailhost',
        widget = atapi.SelectionWidget(
            label = _(u"EasyNewsletter_label_externalDeliveryService",
                default=u"External delivery service"),
            description = _(u"EasyNewsletter_help_externalDeliveryService",
                default=u"Some packages provide an external delivery service \
                    for EasyNewsletter. If one is installed you can choose it here."),
            i18n_domain = 'EasyNewsletter',
            size = 10,
        )
    ),

    ZPTField('out_template_pt',
        schemata = 'settings',
        required = True,
        default = config.DEFAULT_OUT_TEMPLATE_PT,
        validators = ('zptvalidator', ),
        widget = atapi.TextAreaWidget(
            label = _(u"label_out_template_pt",
                default=u"Outgoing Mail Template"),
            description = _(u"help_mailtemplate_body_pt",
                default=u"This is a Zope Page Template used for rendering of the out going mail. \
                You don\'t need to modify it, but if you know TAL (Zope\'s Template \
                Attribute Language) you have the full power to customize your outgoing mails."),
            i18n_domain = "EasyNewsletter",
            rows = 40,
            ),
    ),

    atapi.StringField('subscriber_confirmation_mail_subject',
        schemata = "settings",
        required = True,
        default = config.DEFAULT_SUBSCRIBER_CONFIRMATION_MAIL_SUBJECT,
        widget = atapi.StringWidget(
            label = _(u'EasyNewsletter_label_subscriber_confirmation_mail_subject',
                default=u'Subscriber confirmation mail subject'),
            description = _(u'EasyNewsletter_description_subscriber_confirmation_mail_subject',
                default=u'Text used for confirmation email subject. You can \
                    customize the text, but it should include the placeholder: ${portal_url}!'),
            i18n_domain = 'EasyNewsletter',
        ),
    ),

    atapi.TextField('subscriber_confirmation_mail_text',
        schemata = "settings",
        required = True,
        default = config.DEFAULT_SUBSCRIBER_CONFIRMATION_MAIL_TEXT,
        widget = atapi.TextAreaWidget(
            rows = 8,
            label = _(u'EasyNewsletter_label_subscriber_confirmation_mail_text',
                default=u'Subscriber confirmation mail text'),
            description = _(u'description_subscriber_confirmation_mail_text',
                default=u'Text used for confirmation email. You can customize \
                    the text, but it should include the placeholders: \
                    ${portal_url}, ${subscriber_email} and ${confirmation_url}!'),
            i18n_domain = 'EasyNewsletter',
        ),
    ),
),
)


schema = ATTopicSchema.copy() + schema
schema['text'].widget.description = _(u'description_text',
    default=u'This is used in the frontpage of EasyNewsletter on top of Issue archive list.')

schema['limitNumber'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['itemCount'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['customView'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['customViewFields'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['allowDiscussion'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['subject'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['location'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['effectiveDate'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['expirationDate'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['creators'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['contributors'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['rights'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}

schema['relatedItems'].schemata = "settings"
schema['language'].schemata = "settings"
schema['excludeFromNav'].schemata = "settings"
schema.moveField('deliveryService', pos='bottom')
schema.moveField('subscriberSource', pos='bottom')
schema.moveField('relatedItems', pos='bottom')
schema.moveField('language', pos='bottom')
schema.moveField('excludeFromNav', pos='bottom')


class EasyNewsletter(ATTopic, atapi.BaseFolder):
    """A folder for managing and archiving newsletters.
    """
    implements(IEasyNewsletter)
    security = ClassSecurityInfo()
    schema = schema
    _at_rename_after_creation = True

    security.declarePublic("initializeArchetype")
    def initializeArchetype(self, **kwargs):
        """Overwritten hook.
        """
        ATTopic.initializeArchetype(self, **kwargs)
        # Add default template
        if not getattr(self, 'default_template', None):
            self.manage_addProduct["EasyNewsletter"].addENLTemplate(id="default_template", title="Default")
        tmpl = self.default_template

    security.declarePublic("displayContentsTab")
    def displayContentsTab(self):
        """Overwritten to hide contents tab.
        """
        return False

    security.declarePublic('addSubscriber')
    def addSubscriber(self, subscriber, fullname, organization, salutation=None):
        """Adds a new subscriber to the newsletter (if valid).
        """
        # we need the subscriber email here as an id, to check for existing entries
        email = subscriber
        plone_utils = getToolByName(self, 'plone_utils')
        subscriber_id = plone_utils.normalizeString(email)
        portal = getToolByName(self, 'portal_url').getPortalObject()
        try:
            execute_under_special_role(portal, "Contributor", self.invokeFactory, "ENLSubscriber", id=subscriber_id, language=self.Language())
        except BadRequest:
            return (False, "email_exists")
        o = getattr(self, subscriber_id)
        o.setEmail(subscriber)
        o.setFullname(fullname)
        o.setOrganization(organization)
        o.setSalutation(salutation)
        o.reindexObject()

        return (True, "subscription_confirmed")

    def getSubTopics(self):
        """Returns sub topics.
        """
        return self.objectValues("ATTopic")

    def get_plone_members(self):
        """ return filtered list of plone members as DisplayList
        """
        global fmp_tool
        if fmp_tool and queryUtility(IFastmemberpropertiesTool, 'fastmemberproperties_tool'):
            log.debug("Use fastmemberpropertiestool to get memberproperties!")
            fmp_tool = queryUtility(IFastmemberpropertiesTool, 'fastmemberproperties_tool')
            member_properties = fmp_tool.get_all_memberproperties()
        else:
            log.info("We use plone API to get memberproperties, this is very \
                slow on many members, please install inqbus.plone.fastmemberproperties to make it fast!")
            acl_userfolder = getToolByName(self, 'acl_users')
            member_objs = acl_userfolder.getUsers()
            member_properties = {}
            for member in member_objs:
                probdict = {}
                probdict['id'] = member.getUserId()
                probdict['email'] = member.getProperty('email')
                probdict['fullname'] = safe_unicode(member.getProperty('fullname'))
                member_properties[probdict['id']] = probdict
        if not member_properties:
            return []
        try:
            results = atapi.DisplayList([(id, property['fullname'] + ' - ' + property['email'])
                                   for id, property in member_properties.items()
                if config.EMAIL_RE.findall(property['email'])])
        except TypeError, e:
            log.error(":get_plone_members: error in member_properties %s/ \
                properties:'%s'" % (e, member_properties.items()))
        # run registered member filter:
        for subscriber in subscribers([self], IReceiversMemberFilter):
            results = subscriber.filter(results)
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
        results = atapi.DisplayList([(id, property['title']) for id, property in group_properties.items()])
        # run registered group filter:
        for subscriber in subscribers([self], IReceiversGroupFilter):
            results = subscriber.filter(results)
        return results.sortedByValue()

    def getNewsletter(self):
        """ return the (parent) Newsletter instance using Acquisition """
        return self

    def get_subscriber_sources(self):
        result = atapi.DisplayList()
        result.add(u'default', _(u'EasyNewsletter_label_noSource', u'no external subscriber source'))
        for utility in getUtilitiesFor(ISubscriberSource):
            result.add(utility[0], utility[0])
        return result

    def get_delivery_services(self):
        result = atapi.DisplayList()
        result.add(u'mailhost', _(u'EasyNewsletter_label_PloneMailHost', u'Default Plone Mailhost'))
        for utility in getUtilitiesFor(IMailHost):
            if utility[0]:
                result.add(utility[0], utility[0])
        return result


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

    @param portal: Reference to ISiteRoot object whose access controls we are using
    @param function: Method to be called with special priviledges
    @param role: User role we are using for the security context when calling \
                 the priviledged code. For example, use "Manager".
    @param args: Passed to the function
    @param kwargs: Passed to the function
    """

    sm = getSecurityManager()
    try:
        try:
            # Clone the current access control user and assign a new role for him/her
            # Note that the username (getId()) is left in exception tracebacks in error_log
            # so it is important thing to store
            tmp_user = UnrestrictedUser(
              sm.getUser().getId(),
               '', [role],
               '')

            # Act as user of the portal
            tmp_user = tmp_user.__of__(portal.acl_users)
            newSecurityManager(None, tmp_user)

            # Call the function
            return function(*args, **kwargs)

        except:
            # If special exception handlers are needed, run them here
            raise
    finally:
        # Restore the old security manager
        setSecurityManager(sm)
