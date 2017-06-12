# -*- coding: utf-8 -*-
# from plone.protect.auto import safeWrite
from AccessControl import ClassSecurityInfo
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from email.Header import Header
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from plone import api
from plone.app.blob.field import ImageField
from plone.registry.interfaces import IRegistry
from Products.Archetypes import atapi
from Products.ATContentTypes.content.topic import ATTopic
from Products.ATContentTypes.content.topic import ATTopicSchema
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _
from Products.EasyNewsletter.config import EMAIL_RE
from Products.EasyNewsletter.config import IS_PLONE_5
from Products.EasyNewsletter.config import PROJECTNAME
from Products.EasyNewsletter.interfaces import IENLIssue
from Products.EasyNewsletter.interfaces import IIssueDataFetcher
from Products.EasyNewsletter.interfaces import IReceiversPostSendingFilter
from Products.EasyNewsletter.interfaces import ISubscriberSource
from Products.EasyNewsletter.queue.interfaces import IIssueQueue
from Products.EasyNewsletter.utils.mail import get_email_charset
from Products.MailHost.interfaces import IMailHost
from zope.component import getUtility
from zope.component import queryUtility
from zope.component import subscribers
from zope.interface import implementer
from zope.site.hooks import getSite
import logging
import pkg_resources
import transaction


try:
    pkg_resources.get_distribution('inqbus.plone.fastmemberproperties')
except pkg_resources.DistributionNotFound:
    fmp_tool = False
else:
    from inqbus.plone.fastmemberproperties.interfaces import (
        IFastmemberpropertiesTool
    )
    fmp_tool = True


if IS_PLONE_5:
    from Products.Archetypes.atapi import TinyMCEWidget as RichTextWidget
else:
    from Products.Archetypes.atapi import RichWidget as RichTextWidget


log = logging.getLogger('Products.EasyNewsletter')


schema = atapi.Schema((
    atapi.TextField(
        'text',
        allowable_content_types=(
            'text/html', 'text/x-plone-outputfilters-html'),
        default_output_type='text/x-plone-outputfilters-html',
        widget=RichTextWidget(
            rows=30,
            label=_('EasyNewsletter_label_text', default=u'Text'),
            description=_(
                u'description_text_issue',
                default=u'The main content of the mailing. You can use \
                    the Collections to collect content or put manual \
                    content in. This will included in outgoing mails.'),
            i18n_domain='EasyNewsletter',
        ),
    ),

    atapi.BooleanField(
        'excludeAllSubscribers',
        default_method='get_excludeAllSubscribers_defaults',
        widget=atapi.BooleanWidget(
            label=_(
                u'label_excludeAllExternalSubscribers',
                default=u'Exclude all external subscribers'),
            description=_(
                u'EasyNewsletter_ENLIssue_help_excludeAllSubscribers',
                default=u'If checked, the newsletter/mailing will not be send  \
                   to all external subscribers inside the newsletter.'),
            i18n_domain='EasyNewsletter',
        )
    ),

    atapi.BooleanField(
        'sendToAllPloneMembers',
        default_method='get_sendToAllPloneMembers_defaults',
        widget=atapi.BooleanWidget(
            label=_(
                u'label_sendToAllPloneMembers',
                default=u'Send to all Plone members'),
            description=_(
                u'EasyNewsletter_ENLIssue_help_sendToAllPloneMembers',
                default=u'If checked, the newsletter/mailing is send to all \
                    plone members.'),
            i18n_domain='EasyNewsletter',
        )
    ),

    atapi.LinesField(
        'ploneReceiverMembers',
        vocabulary='get_plone_members',
        default_method='get_ploneReceiverMembers_defaults',
        widget=atapi.MultiSelectionWidget(
            label=_(
                u'EasyNewsletter_label_ploneReceiverMembers',
                default=u'Plone Members to receive the newsletter'),
            description=_(
                u'EasyNewsletter_ENLIssue_help_ploneReceiverMembers',
                default=u'Choose Plone Members which should receive \
                        the newsletter.'),
            i18n_domain='EasyNewsletter',
            size=20,
        )
    ),

    atapi.LinesField(
        'ploneReceiverGroups',
        vocabulary='get_plone_groups',
        default_method='get_ploneReceiverGroups_defaults',
        widget=atapi.MultiSelectionWidget(
            label=_(
                u'EasyNewsletter_label_ploneReceiverGroups',
                default=u'Plone Groups to receive the newsletter'),
            description=_(
                u'EasyNewsletter_ENLIssue_help_ploneReceiverGroups',
                default=u'Choose Plone Groups which members should \
                        receive the newsletter.'),
            i18n_domain='EasyNewsletter',
            size=10,
        )
    ),

    atapi.ReferenceField(
        'contentAggregationSources',
        schemata='settings',
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

    atapi.BooleanField(
        'hideImage',
        schemata='settings',
        default=False,
        widget=atapi.BooleanWidget(
            label=_(
                u'label_issueHideImage',
                default=u'Hide banner image.'),
            description=_(
                u'enl_issue_help_hide_image',
                default=u'If checked, the banner image defined on newsletter \
                    or on this issue will not be used.'),
            i18n_domain='EasyNewsletter',
        )
    ),

    ImageField(
        'image',
        schemata='settings',
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

    atapi.TextField(
        'header',
        schemata='settings',
        allowable_content_types=(
            'text/html', 'text/x-plone-outputfilters-html'),
        default_output_type='text/x-plone-outputfilters-html',
        default_method='get_default_header',
        widget=RichTextWidget(
            rows=10,
            label=_(
                u'EasyNewsletter_label_header',
                default=u'Header'),
            description=_(
                u'description_help_header',
                default=u'The header will included in outgoing mails.'),
            i18n_domain='EasyNewsletter',
        ),
    ),

    atapi.TextField(
        'footer',
        schemata='settings',
        allowable_content_types=(
            'text/html', 'text/x-plone-outputfilters-html'),
        default_output_type='text/x-plone-outputfilters-html',
        default_method='get_default_footer',
        widget=RichTextWidget(
            rows=10,
            label=_(u'EasyNewsletter_label_footer', default=u'Footer'),
            description=_(
                u'description_help_footer',
                default=u'The footer will included in outgoing mails.'),
            i18n_domain='EasyNewsletter',
        ),
    ),

    atapi.StringField(
        'template',
        schemata='settings',
        default_method='get_aggregation_template_from_parent',
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

    atapi.StringField(
        'outputTemplate',
        vocabulary="get_output_templates",
        required=True,
        default_method='get_output_template_from_parent',
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

),
)

schema = ATTopicSchema.copy() + schema

# hide id, even if visible_ids is True
schema['id'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
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

schema.moveField('header', pos='bottom')
schema.moveField('footer', pos='bottom')
schema.moveField('relatedItems', pos='bottom')
schema.moveField('language', pos='bottom')


@implementer(IENLIssue)
class ENLIssue(ATTopic, atapi.BaseContent):
    """A newsletter which can be send to subscribers.
    """
    security = ClassSecurityInfo()
    schema = schema

    def get_aggregation_template_objects(self):
        enl = self.getNewsletter()
        return enl.objectValues('ENLTemplate')

    def get_aggregation_template_from_parent(self):
        enl = self.getNewsletter()
        return enl.getTemplate()

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

    def get_output_template_from_parent(self):
        enl = self.getNewsletter()
        return enl.getOutputTemplate()

    def has_image(self):
        has_image = bool(self.get_image_src())
        return has_image

    def has_logo(self):
        enl = self.getNewsletter()
        has_logo = getattr(enl.aq_explicit, 'logo', None)
        return has_logo

    def get_image_src(self):
        img_src = ""
        if self.getHideImage():
            return img_src
        scales = self.restrictedTraverse('@@images')
        if scales.scale('image', scale='mini'):
            img_src = self.absolute_url() + "/image"
            return img_src
        enl = self.getNewsletter()
        scales = enl.restrictedTraverse('@@images')
        if scales.scale('image', scale='mini'):
            img_src = enl.absolute_url() + "/image"
        return img_src

    def _get_salutation_mappings(self):
        """
        returns mapping of salutations. Each salutation itself is a dict
        with key as language. (prepared for multilingual newsletter)
        """
        enl = self.getNewsletter()
        result = {}
        lang = self.Language() or 'en'

        for line in enl.getSalutations():
            if "|" not in line:
                continue
            key, value = line.split('|')
            result[key.strip()] = {lang: value.strip()}
        return result

    def _send_recipients(self):
        """ return list of recipients """
        request = self.REQUEST
        enl = self.getNewsletter()
        salutation_mappings = self._get_salutation_mappings()
        if getattr(request, 'test', None):
            # get test e-mail
            test_receiver = request.get('test_receiver', '')
            if test_receiver == "":
                test_receiver = enl.getTestEmail()
            salutation = salutation_mappings.get('default', '')
            receivers = [{
                'email': test_receiver,
                'fullname': 'Test Member',
                'salutation': salutation.get(self.Language(), ''),
                'nl_language': self.Language()
            }]
            return receivers

        # only send to all subscribers if the exclude all subscribers
        # checkbox, was not set.
        # get ENLSubscribers
        enl_receivers = []
        if not self.getExcludeAllSubscribers():
            for subscriber in enl.objectValues('ENLSubscriber'):
                salutation_key = subscriber.getSalutation()
                salutation = salutation_mappings.get(salutation_key, {})
                enl_receivers.append({
                    'email': subscriber.getEmail(),
                    'gender': subscriber.getSalutation(),
                    'name_prefix': subscriber.getName_prefix(),
                    'firstname': subscriber.getFirstname(),
                    'lastname': subscriber.getLastname(),
                    'fullname': ' '.join([subscriber.getFirstname(),
                                          subscriber.getLastname()]),
                    'salutation': salutation.get(
                        subscriber.getNl_language(),
                        salutation.get(self.Language() or 'en', '')
                    ),
                    'uid': subscriber.UID(),
                    'nl_language': subscriber.getNl_language()})

        # get subscribers over selected plone members and groups
        plone_receivers = self.get_plone_subscribers()
        external_subscribers = self._get_external_source_subscribers(enl)
        receivers_raw = plone_receivers + enl_receivers + \
            external_subscribers
        receivers = self._unique_receivers(receivers_raw)

        return receivers

    def _get_external_source_subscribers(self, enl):
        external_subscribers = []
        external_source_name = enl.getSubscriberSource()
        if external_source_name == 'default':
            return external_subscribers
        log.info(
            'Searching for users in external source "%s"' %
            external_source_name)
        external_source = queryUtility(
            ISubscriberSource, name=external_source_name)
        if external_source:
            external_subscribers = external_source.getSubscribers(enl)
            log.info('Found %d external subscriptions' % len(
                external_subscribers))
        return external_subscribers

    def _unique_receivers(self, receivers_raw):
        receivers = []
        mails = []
        for receiver in receivers_raw:
            if receiver['email'] in mails:
                continue
            mails.append(receiver['email'])
            receivers.append(receiver)
        return receivers

    def getText(self):
        output_html = self.getRawText()
        # we want pnly apply plone-outputfilters here,
        # but not the safe-html filter!
        resolved_html = str(self.portal_transforms.convertTo(
            'text/x-plone-outputfilters-html',
            output_html, encoding="utf8",
            mimetype='text/html', context=self))
        return resolved_html

    @property
    def issue_queue(self):
        return queryUtility(IIssueQueue)

    @security.protected('Modify portal content')
    def queue_issue_for_sendout(self):
        """queues this issue for sendout using zamqp
        """
        queue = self.issue_queue
        if queue is None:
            raise NotImplemented(
                'One need to install and configure a queue in '
                'order to use the feature of a queued sendout.'
            )

        # check for workflow
        current_state = api.content.get_state(obj=self)
        if current_state != 'sending':
            raise ValueError(
                'Executed queue issue for sendout in wrong review state!'
            )
        queue.start(self)

    @security.protected('Modify portal content')
    def send(self, recipients=[]):
        """Sends the newsletter.
           An optional list of dicts (keys=fullname|mail) can be passed in
           for sending a newsletter out addresses != subscribers.
        """
        # preparations
        request = self.REQUEST
        test = hasattr(request, 'test')
        current_state = api.content.get_state(obj=self)

        # check for workflow
        if not (test or recipients) and current_state != 'sending':
            raise ValueError('Executed send in wrong review state!')

        # get hold of the parent Newsletter object#
        enl = self.getNewsletter()

        # get sender name
        sender_name = request.get('sender_name')
        if not sender_name:
            sender_name = enl.getSenderName()
        # don't use Header() with a str and a charset arg, even if
        # it is correct this would generate a encoded header and mail
        # server may not support utf-8 encoded header
        from_header = Header(safe_unicode(sender_name))

        # get sender e-mail
        sender_email = request.get('sender_email')
        if not sender_email:
            sender_email = enl.getSenderEmail()
        from_header.append(u'<%s>' % safe_unicode(sender_email))

        # determine MailHost first (build-in vs. external)
        deliveryServiceName = enl.getDeliveryService()
        if deliveryServiceName == 'mailhost':
            mail_host = getToolByName(enl, 'MailHost')
        else:
            mail_host = getUtility(IMailHost, name=deliveryServiceName)
        log.info('Using mail delivery service "%r"' % mail_host)

        send_counter = 0
        send_error_counter = 0

        charset = get_email_charset()
        if not recipients:
            receivers = self._send_recipients()
        issue_data_fetcher = IIssueDataFetcher(self)
        for receiver in receivers:
            # get complete issue data
            issue_data = issue_data_fetcher(receiver)

            # create multipart mail
            outer = MIMEMultipart('alternative')
            outer['To'] = Header(u'<%s>' % safe_unicode(receiver['email']))
            outer['From'] = from_header
            outer['Subject'] = issue_data['subject_header']
            outer.epilogue = ''

            # Attach text part
            text_part = MIMEText(issue_data['body_plain'], 'plain', charset)

            # Attach html part with images
            html_part = MIMEMultipart('related')
            html_text = MIMEText(issue_data['body_html'], 'html', charset)
            html_part.attach(html_text)

            # Add images to the message
            for image in issue_data['images_to_attach']:
                html_part.attach(image)
            outer.attach(text_part)
            outer.attach(html_part)

            try:
                mail_host.send(outer.as_string())
                log.info('Send newsletter to "%s"' % receiver['email'])
                send_counter += 1
            except Exception, e:  # noqa
                log.exception(
                    'Sending newsletter to "%s" failed, with error "%s"!'
                    % (receiver['email'], e))
                send_error_counter += 1

        log.info(
            'Newsletter was sent to (%s) receivers. (%s) errors occurred!'
            % (send_counter, send_error_counter))

        # change status only for a 'regular' send operation (not 'test', no
        # explicit recipients)
        if not (test or recipients):
            request['enlwf_guard'] = True
            api.content.transition(obj=self, transition='sending_completed')
            request['enlwf_guard'] = False

    @security.protected('Modify portal content')
    def loadContent(self):
        """ Agregate content from content_aggregation_sources.
        """
        # issue_template = self.restrictedTraverse(self.getTemplate())
        enl_template_obj_id = self.getTemplate()
        enl = self.getNewsletter()
        if enl_template_obj_id not in enl.objectIds():
            log.warn("No enl_template found, skip loadContent!")
            return
        issue_template = getattr(enl.aq_explicit, enl_template_obj_id, None)

        # here we create a write on read, but we do not need to persist it:
        sp = transaction.savepoint()
        issue_template.setIssue(self.UID())
        portal = getSite()
        template_id = issue_template.getAggregationTemplate()
        if template_id != 'custom':
            template_obj = portal.restrictedTraverse(template_id)
            # XXX we copy over the template here every time we load the content
            # which is not perfect but ok for now.
            # This will be refactored when we drop Plone 4 support and use
            # behaviors on source object like Collections
            issue_template.setBody(template_obj.read())
        text = issue_template.body()
        sp.rollback()
        self.setText(text)

    def get_default_header(self):
        enl = self.getNewsletter()
        return enl.getRawDefault_header()

    def get_default_footer(self):
        enl = self.getNewsletter()
        return enl.getRawDefault_footer()

    def get_plone_members(self):
        enl = self.getNewsletter()
        return enl.get_plone_members()

    def get_plone_groups(self):
        enl = self.getNewsletter()
        return enl.get_plone_groups()

    def get_excludeAllSubscribers_defaults(self):
        enl = self.getNewsletter()
        return enl.getExcludeAllSubscribers()

    def get_sendToAllPloneMembers_defaults(self):
        enl = self.getNewsletter()
        return enl.getSendToAllPloneMembers()

    def get_ploneReceiverMembers_defaults(self):
        """ return all selected members from parent newsletter object.
        """
        enl = self.getNewsletter()
        return enl.getPloneReceiverMembers()

    def get_ploneReceiverGroups_defaults(self):
        """ return all selected groups from parent newsletter object.
        """
        enl = self.getNewsletter()
        return enl.getPloneReceiverGroups()

    def get_plone_subscribers(self):
        """ Search for all selected Members and Groups
            and return a filtered list of subscribers as dicts.
        """
        global fmp_tool
        enl = self.getNewsletter()
        plone_subscribers = []
        if self.getSendToAllPloneMembers():
            log.info(
                "SendToAllPloneMembers is true, so we add all existing"
                " members to receiver_member_list!")
            receiver_member_list = enl.get_plone_members()
            # if all members are receivers we don't need groups relations:
            receiver_group_list = []
        else:
            receiver_member_list = self.getPloneReceiverMembers()
            receiver_group_list = self.getPloneReceiverGroups()
        gtool = getToolByName(self, 'portal_groups')
        if fmp_tool:
            fmp_tool = queryUtility(
                IFastmemberpropertiesTool,
                'fastmemberproperties_tool'
            )
            # use fastmemberproperties to get mememberproperties:
            member_properties = fmp_tool.get_all_memberproperties()
        else:
            # use plone API to get memberproperties,
            # works without fastmemberproperties, but is much slower!
            acl_userfolder = getToolByName(self, 'acl_users')
            member_objs = acl_userfolder.getUsers()
            member_properties = {}
            for member in member_objs:
                probdict = {}
                probdict['id'] = member.getUserId()
                probdict['email'] = member.getProperty('email')
                probdict['gender'] = member.getProperty('nl_gender', 'default')
                # try last name first
                probdict['fullname'] = member.getProperty(
                    'last_name',
                    member.getProperty('fullname')
                )
                probdict['language'] = member.getProperty('language')
                # fallback for default plone users without a enl language
                if not probdict['language']:
                    probdict['language'] = self.Language()
                member_properties[probdict['id']] = probdict
        if not member_properties:
            return []
        selected_group_members = []
        for group in receiver_group_list:
            selected_group_members.extend(gtool.getGroupMembers(group))
        receiver_member_list = receiver_member_list + tuple(
            selected_group_members
        )

        # get salutation mappings
        salutation_mappings = self._get_salutation_mappings()
        # get all selected member properties
        for receiver_id in set(receiver_member_list):
            if receiver_id not in member_properties:
                log.debug(
                    "Ignore reveiver \"%s\", because we have "
                    "no properties for this member!" % receiver_id)
                continue
            member_property = member_properties[receiver_id]
            if EMAIL_RE.findall(member_property['email']):
                salutation = salutation_mappings[
                    member_property.get('gender', 'default')
                ]
                plone_subscribers.append({
                    'fullname': member_property['fullname'],
                    'email': member_property['email'],
                    'salutation': salutation.get(
                        member_property.get('language', ''),
                        salutation.get(self.Language() or 'en', 'unset')
                    ),
                    'nl_language': member_property.get('language', '')
                })
            else:
                log.debug(
                    "Skip '%s' because \"%s\" is not a real email!"
                    % (receiver_id, member_property['email']))
        # run registered receivers post sending filters:
        for subscriber in subscribers([enl], IReceiversPostSendingFilter):
            plone_subscribers = subscriber.filter(plone_subscribers)
        return plone_subscribers

    def getFiles(self):
        """ Return list of files in subtree """
        return self.getFolderContents(
            contentFilter=dict(
                portal_type=('File'),
                sort_on='getObjPositionInParent'
            )
        )


atapi.registerType(ENLIssue, PROJECTNAME)
