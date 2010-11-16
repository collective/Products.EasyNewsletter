# python imports
import formatter
import cStringIO
from htmllib import HTMLParser
from urlparse import urlparse
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEImage import MIMEImage
from email.Header import Header
from email import Encoders

# zope imports
from zope.interface import implements
from zope.component import queryUtility
from zope.component import getUtility, ComponentLookupError
from Acquisition import aq_parent, aq_inner

# Zope / Plone import
from AccessControl import ClassSecurityInfo
from Products.MailHost.interfaces import IMailHost
from Products.Archetypes.atapi import *
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _
from Products.EasyNewsletter.interfaces import ISubscriberSource
from Products.ATContentTypes.content.topic import ATTopic
from Products.ATContentTypes.content.topic import ATTopicSchema
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.Archetypes.public import ObjectField

try:
    from inqbus.plone.fastmemberproperties.interfaces import IFastmemberpropertiesTool
    fmp_tool = queryUtility(IFastmemberpropertiesTool, 'fastmemberproperties_tool')
    no_fmp = not(fmp_tool)
except:
    no_fmp = True


# EasyNewsletter imports
from Products.EasyNewsletter.interfaces import IENLIssue
from Products.EasyNewsletter.config import PROJECTNAME, EMAIL_RE
from Products.EasyNewsletter.utils.ENLHTMLParser import ENLHTMLParser
from Products.EasyNewsletter.content.ENLSubscriber import ENLSubscriber

import logging

log = logging.getLogger("Products.EasyNewsletter")


schema=Schema((

    TextField('header',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword',),
        default_method = "get_default_header",
        widget=RichWidget(
            rows=10,
            label='Header',
            label_msgid='EasyNewsletter_label_header',
            description=_(u'description_help_header', default=u'The header will included in outgoing mails.'),
            description_msgid='EasyNewsletter_help_header',
            i18n_domain='EasyNewsletter',
        ),
        default_output_type='text/html'
    ),

    TextField('text',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword',),
        widget=RichWidget(
            rows=30,
            label='Text',
            label_msgid='EasyNewsletter_label_text',
            description=_(u'description_text_issue', default=u'The main content of the mailing. You can use the topic criteria to collect content or put manual content in. This will included in outgoing mails.'),
            description_msgid='EasyNewsletter_help_text',
            i18n_domain='EasyNewsletter',
        ),
        default_output_type='text/html'
    ),

    TextField('footer',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword',),
        default_method = "get_default_footer",
        widget=RichWidget(
            rows=10,
            label='Footer',
            label_msgid='EasyNewsletter_label_footer',
            description=_(u'description_help_footer', default=u'The footer will included in outgoing mails.'),
            description_msgid='EasyNewsletter_help_footer',
            i18n_domain='EasyNewsletter',
        ),
        default_output_type='text/html'
    ),

    BooleanField('acquireCriteria',
        default="True",
        widget=BooleanWidget(
            label=_(u'label_inherit_criteria', default=u'Inherit Criteria'),
            description_msgid='EasyNewsletter_help_acquireCriteria',
            i18n_domain='EasyNewsletter',
        )
    ),

    # Overwritten to adapt attribute from ATTopic
    StringField('template',
        default="default_template",
        widget=StringWidget(
            macro="NewsletterTemplateWidget",
            label="Newsletter Template",
            description="Template, to generate the newsletter.",
            label_msgid='EasyNewsletter_label_template',
            description_msgid='EasyNewsletter_help_template',
            i18n_domain='EasyNewsletter',
        ),
        required=1
    ),

    # Overwritten to hide attribute from ATTopic
    BooleanField('limitNumber',
        widget=BooleanWidget(
            visible={'edit':'hidden', 'view':'hidden'},
            label='Limitnumber',
            label_msgid='EasyNewsletter_label_limitNumber',
            description_msgid='EasyNewsletter_help_limitNumber',
            i18n_domain='EasyNewsletter',
        )
    ),

    # Overwritten to hide attribute from ATTopic
    BooleanField('itemCount',
        widget=BooleanWidget(
            visible={'edit':'hidden', 'view':'hidden'},
            label='Itemcount',
            label_msgid='EasyNewsletter_label_itemCount',
            description_msgid='EasyNewsletter_help_itemCount',
            i18n_domain='EasyNewsletter',
        )
    ),

    # Overwritten to hide attribute from ATTopic
    BooleanField('customView',
        widget=BooleanWidget(
            visible={'edit':'hidden', 'view':'hidden'},
            label='Customview',
            label_msgid='EasyNewsletter_label_customView',
            description_msgid='EasyNewsletter_help_customView',
            i18n_domain='EasyNewsletter',
        )
    ),

    # Overwritten to hide attribute from ATTopic
    BooleanField('customViewFields',
        widget=BooleanWidget(
            visible={'edit':'hidden', 'view':'hidden'},
            label='Customviewfields',
            label_msgid='EasyNewsletter_label_customViewFields',
            description_msgid='EasyNewsletter_help_customViewFields',
            i18n_domain='EasyNewsletter',
        )
    ),

    LinesField('ploneReceiverMembers',
        vocabulary="get_plone_members",
        default_method="get_ploneReceiverMembers_defaults",
        widget=MultiSelectionWidget(
            label='Plone Members to receive',
            label_msgid='EasyNewsletter_label_ploneReceiverMembers',
            description_msgid='EasyNewsletter_help_ploneReceiverMembers',
            i18n_domain='EasyNewsletter',
            size = 20,
        )
    ),

    LinesField('ploneReceiverGroups',
        vocabulary="get_plone_groups",
        default_method="get_ploneReceiverGroups_defaults",
        widget=MultiSelectionWidget(
            label='Plone Groups to receive',
            label_msgid='EasyNewsletter_label_ploneReceiverGroups',
            description_msgid='EasyNewsletter_help_ploneReceiverGroups',
            i18n_domain='EasyNewsletter',
            size = 10,
        )
    ),
),
)

schema = ATTopicSchema + schema
schema.moveField('text', after='header')
schema.moveField('acquireCriteria', before='template')
# hide id, even if visible_ids is True
schema['id'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}


class ENLIssue(ATTopic, BaseContent):
    """A newsletter which can be send to subscribers.
    """
    implements(IENLIssue)
    security = ClassSecurityInfo()
    schema = schema

    security.declarePublic("initializeArchetype")
    def initializeArchetype(self, **kwargs):
        """Overwritten hook
        """
        ATTopic.initializeArchetype(self, **kwargs)
        self.loadContent()

    security.declarePublic("folder_contents")
    def folder_contents(self):
        """Overwritten to "forbid" folder_contents
        """
        url = self.absolute_url()
        self.REQUEST.RESPONSE.redirect(url)


    def _send_recipients(self, recipients=[]):
        """ return list of recipients """

        request = self.REQUEST
        enl = self.getNewsletter()

        if recipients:
            receivers = recipients

        elif hasattr(request, "test"):
            # get test e-mail
            test_receiver = request.get("test_receiver", "")
            if test_receiver == "":
                test_receiver = enl.getTestEmail()
            receivers = [{'email': test_receiver, 'fullname': ''}]

        else:
            # get ENLSubscribers
            enl_receivers = [{
                'email': subscriber.getEmail(),
                'fullname': subscriber.getFullname(),
                'uid': subscriber.UID()} \
                    for subscriber in enl.objectValues("ENLSubscriber")]
            # get subscribers over selected plone members and groups
            plone_receivers = self.get_plone_subscribers()

            # check external subscriber source
            external_subscribers = []
            external_source_name = enl.getSubscriberSource()
            if external_source_name != 'default':
                log.info('Searching for users in external source "%s"' % external_source_name)
                try:
                    external_source = getUtility(ISubscriberSource, name=external_source_name)
                    external_subscribers = external_source.getSubscribers(enl)
                    log.info('Found %d external subscriptions' % len(external_subscribers))
                except ComponentLookupError:
                    pass
            receivers = plone_receivers + enl_receivers + external_subscribers

        return receivers

    def _send_body(self):
        """ Return rendered body of newsletter (text+html) 
            w/o header and footer.
        """

        enl = self.getNewsletter()

        # get charset
        props = getToolByName(self, "portal_properties").site_properties
        charset = props.getProperty("default_charset")
        # get out_template from ENL object and render it in context of issue
        out_template_pt_field = enl.getField('out_template_pt')
        ObjectField.set(out_template_pt_field, self, ZopePageTemplate(out_template_pt_field.getName(), enl.getRawOut_template_pt()))
        output_html = self.out_template_pt.pt_render().encode(charset)
        # remove >>PERSOLINE>> marker
        text = output_html.replace("<p>&gt;&gt;PERSOLINE&gt;&gt;", "")
        # exchange relative URLs
        parser_output_zpt = ENLHTMLParser(self)
        parser_output_zpt.feed(text)
        text = parser_output_zpt.html
        text_plain = self.create_plaintext_message(text)
        image_urls = parser_output_zpt.image_urls
        return dict(html=text, plain=text_plain, images=image_urls)

    security.declarePublic('send')
    def send(self, recipients=[]):
        """Sends the newsletter.
           An optional list of dicts (keys=fullname|mail) can be passed in 
           for sending a newsletter out addresses != subscribers.
        """

        # preparations
        request = self.REQUEST

        # get hold of the parent Newsletter object#       
        enl = self.getNewsletter()

        # get sender name
        sender_name = request.get("sender_name", "")
        if sender_name == "":
            sender_name = enl.getSenderName()

        # get sender e-mail
        sender_email = request.get("sender_email", "")
        if sender_email == "":
            sender_email = enl.getSenderEmail()

        # get subject
        subject = request.get("subject", "")
        if subject == "":
            subject = self.Title()

        # Create from-header
        from_header = enl.getSenderName() and '"%s" <%s>' % (sender_name, sender_email) or sender_email

        # determine MailHost first (build-in vs. external)
        deliveryServiceName = enl.getDeliveryService()
        if deliveryServiceName == 'mailhost':
            MailHost = getToolByName(enl, 'MailHost')
        else:
            MailHost = getUtility(IMailHost, name=deliveryServiceName)
        log.info('Using mail delivery service "%r"' % MailHost)

        send_counter = 0
        send_error_counter = 0

        receivers = self._send_recipients(recipients)
        send_body = self._send_body()
        text = send_body['html']
        text_plain = send_body['plain']
        image_urls = send_body['images']
        props = getToolByName(self, "portal_properties").site_properties
        charset = props.getProperty("default_charset")

        for receiver in receivers:
            # create multipart mail
            mail = MIMEMultipart("alternative")

            if hasattr(request, "test"):
                mail['To'] = receiver['email']
                fullname = "Test Member"
                personal_text = text.replace("{% unsubscribe %}", "")
                personal_text_plain = text_plain.replace("{% unsubscribe %}", "")
            else:
                if receiver.has_key('uid'):
                    try:
                        unsubscribe_text = enl.getUnsubscribe_string()
                    except AttributeError:
                        unsubscribe_text = "Click here to unsubscribe"
                    unsubscribe_link = enl.absolute_url() + "/unsubscribe?subscriber=" + receiver['uid']
                    personal_text = text.replace("{% unsubscribe %}", """<a href="%s">%s.</a>""" % (unsubscribe_link, unsubscribe_text))
                    personal_text_plain = text_plain.replace("{% unsubscribe %}", """%s: %s""" % (unsubscribe_text, unsubscribe_link))
                else:
                    personal_text = text.replace("{% unsubscribe %}", "")
                    personal_text_plain = text_plain.replace("{% unsubscribe %}", "")

                fullname = receiver['fullname']
                if not fullname:
                    try:
                        fullname = enl.getFullname_fallback()
                    except AttributeError:
                        fullname = "Sir or Madam"
                mail['To'] = receiver['email']

            personal_text = personal_text.replace("{% subscriber-fullname %}", fullname)
            personal_text_plain = personal_text_plain.replace("{% subscriber-fullname %}", fullname)

            mail['From']    = from_header
            mail['Subject'] = Header(subject)
            mail.epilogue   = ''

            # Attach text part
            text_part = MIMEText(personal_text_plain, "plain", charset)
            mail.attach(text_part)

            # Attach html part with images
            html_part = MIMEMultipart("related")
            html_text = MIMEText(personal_text, "html", charset)
            html_part.attach(html_text)

            # Add images to the message
            image_number = 0
            for image_url in image_urls:
                image_url = urlparse(image_url)[2]
                o = self.restrictedTraverse(image_url)
                if hasattr(o, "_data"):                               # file-based
                    image = MIMEImage(o._data)
                else:
                    image = MIMEImage(o.data)                         # zodb-based
                image["Content-ID"] = "image_%s" % image_number
                image_number += 1
                html_part.attach(image)

            mail.attach(html_part)
            try:
                MailHost.send(mail.as_string())
                log.info("Send newsletter to \"%s\"" % receiver['email'])
                send_counter += 1
            except Exception, e:
                log.info("Sending newsletter to \"%s\" failt, with error \"%s\"!" % (receiver['email'], e))
                send_error_counter += 1

        log.info("Newsletter was send to (%s) receivers. (%s) errors occurred!" % (send_counter, send_error_counter))

        # change status only for a 'regular' send operation (not 'test', no
        # explicit recipients)
        if not hasattr(request, "test") and not recipients:
            wftool = getToolByName(self, "portal_workflow")
            if wftool.getInfoFor(self, 'review_state') == 'draft':
                wftool.doActionFor(self, "send")

    security.declareProtected("Manage portal", "loadContent")
    def loadContent(self):
        """Loads text dependend on criteria into text attribute.
        """
        issue_template = self.restrictedTraverse(self.getTemplate())
        issue_template.setIssue(self.UID())
        text = issue_template.body()
        self.setText(text)

    def getSubTopics(self):
        """Returns subtopics of the issues.
        """
        topics = self.objectValues("ATTopic")

        if self.getAcquireCriteria():
            return self.aq_inner.aq_parent.objectValues("ATTopic")
        else:
            return topics

    def get_unpersonalized_body(self):
        """
        """
        personalized_body_lines = self.getRawText().split('\r\n')
        unpersonalized_body = '\r\n'.join([line for line in personalized_body_lines if not line.startswith("<p>&gt;&gt;PERSOLINE&gt;&gt;")])
        return unpersonalized_body

    def get_default_header(self):
        newsletter_obj = aq_parent(aq_inner(self))
        return newsletter_obj.getRawDefault_header()

    def get_default_footer(self):
        newsletter_obj = aq_parent(aq_inner(self))
        return newsletter_obj.getRawDefault_footer()

    def get_plone_members(self):
        newsletter_obj = aq_parent(aq_inner(self))
        return newsletter_obj.get_plone_members()

    def get_plone_groups(self):
        newsletter_obj = aq_parent(aq_inner(self))
        return newsletter_obj.get_plone_groups()

    def get_ploneReceiverMembers_defaults(self):
        """ return all selected members from parent newsletter object.
        """
        newsletter_obj = aq_parent(aq_inner(self))
        return newsletter_obj.getPloneReceiverMembers() 

    def get_ploneReceiverGroups_defaults(self):
        """ return all selected groups from parent newsletter object.
        """
        newsletter_obj = aq_parent(aq_inner(self))
        return newsletter_obj.getPloneReceiverGroups() 

    def get_plone_subscribers(self):
        """ Search for all selected Members and Groups
            and return a list of subscribers.
        """
        plone_subscribers = []
        receiver_member_list = self.getPloneReceiverMembers()
        receiver_group_list = self.getPloneReceiverGroups()
        gtool = getToolByName(self, 'portal_groups')
        if not no_fmp:
            # use fastmemberproperties to get mememberproperties: 
            member_properties = fmp_tool.get_all_memberproperties()
        else:
            # use plone API to get memberproperties, works without fastmemberproperties, 
            # but is much slower!
            acl_userfolder = getToolByName(self, 'acl_users')
            member_objs = acl_userfolder.getUsers()
            member_properties = {}
            for member in member_objs:
                probdict = {}
                probdict['id'] = member.getUserId()
                probdict['email'] = member.getProperty('email')
                probdict['fullname'] = member.getProperty('fullname')
                member_properties[probdict['id']] = probdict

        if not member_properties:
            return []
        selected_group_members = []
        for group in receiver_group_list:
            selected_group_members.extend(gtool.getGroupMembers(group))
        receiver_member_list = receiver_member_list + tuple(selected_group_members)
        # get all selected member properties
        for receiver_id in set(receiver_member_list):
            if not member_properties.has_key(receiver_id):
                log.debug("Ignore reveiver \"%s\", because we have no properties for this member!" % receiver_id)
                continue
            member_property = member_properties[receiver_id]
            if EMAIL_RE.findall(member_property['email']):
                plone_subscribers.append({
                    'fullname': member_property['fullname'],
                    'email': member_property['email'],
                })
            else:
                log.debug("Skip '%s' because \"%s\" is not a real email!" % (receiver_id, member_property['email']))
        return plone_subscribers

    def create_plaintext_message(self, text):
        """ Create a plain-text-message by parsing the html
            and attaching links as endnotes 
        """
        plain_text_maxcols = 72
        textout = cStringIO.StringIO()
        formtext = formatter.AbstractFormatter(formatter.DumbWriter(
                        textout, plain_text_maxcols))
        parser = HTMLParser(formtext)
        parser.feed(text)
        parser.close()

        # append the anchorlist at the bottom of a message
        # to keep the message readable.
        counter = 0
        anchorlist  = "\n\n" + ("-" * plain_text_maxcols) + "\n\n"
        for item in parser.anchorlist:
            counter += 1
            anchorlist += "[%d] %s\n" % (counter, item)

        text = textout.getvalue() + anchorlist
        del textout, formtext, parser, anchorlist
        return text

    def getFiles(self):
        """ Return list of files in subtree """
        return self.getFolderContents(contentFilter=dict(portal_type=('File',), 
                                      sort_on='getObjPositionInParent'))

registerType(ENLIssue, PROJECTNAME)
