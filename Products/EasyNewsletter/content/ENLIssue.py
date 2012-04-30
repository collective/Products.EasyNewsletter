import cStringIO
import formatter
import urllib

from htmllib import HTMLParser
from urlparse import urlparse
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEImage import MIMEImage
from email.Header import Header
#from email import Encoders
from stoneagehtml import compactify

from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.Archetypes.public import ObjectField
from Products.ATContentTypes.content.topic import ATTopic
from Products.ATContentTypes.content.topic import ATTopicSchema
from Products.CMFCore.utils import getToolByName
from Products.MailHost.interfaces import IMailHost
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

from zope.component import queryUtility
from zope.component import getUtility
from zope.component import subscribers
from zope.interface import implements

try:
    from inqbus.plone.fastmemberproperties.interfaces import IFastmemberpropertiesTool
    fmp_tool = True
except:
    fmp_tool = False

from Products.EasyNewsletter import EasyNewsletterMessageFactory as _
from Products.EasyNewsletter.config import PROJECTNAME, EMAIL_RE
from Products.EasyNewsletter.interfaces import IENLIssue
from Products.EasyNewsletter.interfaces import IReceiversPostSendingFilter
from Products.EasyNewsletter.interfaces import ISubscriberSource
from Products.EasyNewsletter.utils.ENLHTMLParser import ENLHTMLParser
#from Products.EasyNewsletter.utils.mail import create_html_mail
from Products.EasyNewsletter.utils import safe_portal_encoding
from Products.CMFPlone.utils import safe_unicode

import logging
log = logging.getLogger("Products.EasyNewsletter")


schema = atapi.Schema((
    atapi.TextField('text',
        allowable_content_types = ('text/plain', 'text/structured', 'text/html', 'application/msword'),
        default_output_type = 'text/html',
        widget = atapi.RichWidget(
            rows = 30,
            label = _('EasyNewsletter_label_text', default=u'Text'),
            description = _(u'description_text_issue',
                default=u'The main content of the mailing. You can use the topic \
                    criteria to collect content or put manual content in. \
                    This will included in outgoing mails.'),
            i18n_domain = 'EasyNewsletter',
        ),
    ),

    atapi.BooleanField('sendToAllPloneMembers',
        default_method = "get_sendToAllPloneMembers_defaults",
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
        default_method = "get_ploneReceiverMembers_defaults",
        widget = atapi.MultiSelectionWidget(
            label = _(u'EasyNewsletter_label_ploneReceiverMembers',
                default=u'Plone Members to receive the newsletter'),
            description = _(u'EasyNewsletter_help_ploneReceiverMembers',
                default=u'Choose Plone Members which should receive the newsletter.'),
            i18n_domain = 'EasyNewsletter',
            size = 20,
        )
    ),

    atapi.LinesField('ploneReceiverGroups',
        vocabulary = "get_plone_groups",
        default_method = "get_ploneReceiverGroups_defaults",
        widget = atapi.MultiSelectionWidget(
            label = _(u'EasyNewsletter_label_ploneReceiverGroups',
                default=u'Plone Groups to receive the newsletter'),
            description = _(u'EasyNewsletter_help_ploneReceiverGroups',
                default=u'Choose Plone Groups which members should receive the newsletter.'),
            i18n_domain = 'EasyNewsletter',
            size = 10,
        )
    ),

    atapi.TextField('header',
        schemata = "settings",
        allowable_content_types = ('text/plain', 'text/structured', 'text/html', 'application/msword'),
        default_method = "get_default_header",
        default_output_type = 'text/html',
        widget = atapi.RichWidget(
            rows = 10,
            label = _(u'EasyNewsletter_label_header',
                default=u"Header"),
            description=_(u'description_help_header',
                default=u'The header will included in outgoing mails.'),
            i18n_domain='EasyNewsletter',
        ),
    ),

    atapi.TextField('footer',
        schemata = "settings",
        allowable_content_types = ('text/plain', 'text/structured', 'text/html', 'application/msword'),
        default_method = "get_default_footer",
        default_output_type = 'text/html',
        widget = atapi.RichWidget(
            rows = 10,
            label = _(u'EasyNewsletter_label_footer', default=u'Footer'),
            description = _(u'description_help_footer',
                default=u'The footer will included in outgoing mails.'),
            i18n_domain = 'EasyNewsletter',
        ),
    ),

    atapi.BooleanField('acquireCriteria',
        schemata = "settings",
        default = True,
        widget = atapi.BooleanWidget(
            label = _(u'label_inherit_criteria', default=u'Inherit Criteria'),
            description = _(u'EasyNewsletter_help_acquireCriteria',
                default=u""),
            i18n_domain = 'EasyNewsletter',
        )
    ),

    # Overwritten to adapt attribute from ATTopic
    atapi.StringField('template',
        schemata = "settings",
        default = "default_template",
        required = 1,
        widget = atapi.StringWidget(
            macro = "NewsletterTemplateWidget",
            label = _(u"EasyNewsletter_label_template",
                default=u"Newsletter Template"),
            description = _(u"EasyNewsletter_help_template"),
                default=u"Template, to generate the newsletter.",
            i18n_domain = 'EasyNewsletter',
        ),
    ),
),
)

schema = ATTopicSchema.copy() + schema
schema.moveField('acquireCriteria', before='template')

# hide id, even if visible_ids is True
schema['id'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['limitNumber'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['itemCount'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['customView'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
schema['customViewFields'].widget.visible = {'view': 'invisible', 'edit': 'invisible'}

schema.moveField('header', pos='bottom')
schema.moveField('footer', pos='bottom')
schema.moveField('relatedItems', pos='bottom')
schema.moveField('language', pos='bottom')


class ENLIssue(ATTopic, atapi.BaseContent):
    """A newsletter which can be send to subscribers.
    """
    implements(IENLIssue)
    security = ClassSecurityInfo()
    schema = schema

    #def at_post_create_script(self):
    #    """Overwritten hook """
    #    self.loadContent()

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
        salutation_mappings = {}
        for line in enl.getSalutations():
            salutation_key, salutation_value = line.split('|')
            salutation_mappings[salutation_key.strip()] = salutation_value.strip()
        if recipients:
            receivers = recipients

        elif hasattr(request, "test"):
            # get test e-mail
            test_receiver = request.get("test_receiver", "")
            if test_receiver == "":
                test_receiver = enl.getTestEmail()
            salutation = salutation_mappings.get('default', '')
            receivers = [{'email': test_receiver, 'fullname': 'Test Member', 'salutation': salutation}]
        else:
            # get ENLSubscribers
            enl_receivers = []
            for subscriber in enl.objectValues("ENLSubscriber"):
                salutation_key = subscriber.getSalutation()
                if salutation_key:
                    salutation = salutation_mappings.get(salutation_key, '')
                else:
                    salutation = ''
                enl_receivers.append({
                    'email': subscriber.getEmail(),
                    'fullname': subscriber.getFullname(),
                    'salutation': salutation,
                    'uid': subscriber.UID()})

            # get subscribers over selected plone members and groups
            plone_receivers = self.get_plone_subscribers()
            # check external subscriber source
            external_subscribers = []
            external_source_name = enl.getSubscriberSource()
            if external_source_name != 'default':
                log.info('Searching for users in external source "%s"' % external_source_name)
                external_source = queryUtility(ISubscriberSource, name=external_source_name)
                if external_source:
                    external_subscribers = external_source.getSubscribers(enl)
                    log.info('Found %d external subscriptions' % len(external_subscribers))

            receivers_raw = plone_receivers + enl_receivers + external_subscribers

            # Avoid double emails
            receivers = []
            mails = []
            for receiver in receivers_raw:
                if receiver['email'] not in mails:
                    mails.append(receiver['email'])
                    receivers.append(receiver)

        return receivers

    def _render_output_html(self):
        """ Return rendered newsletter
            with header+body+footer (raw html).
        """
        enl = self.getNewsletter()
        props = getToolByName(self, "portal_properties").site_properties
        charset = props.getProperty("default_charset")
        # get out_template from ENL object and render it in context of issue
        out_template_pt_field = enl.getField('out_template_pt')
        ObjectField.set(out_template_pt_field, self, ZopePageTemplate(
            out_template_pt_field.getName(),
            enl.getRawOut_template_pt()))
        output_html = safe_portal_encoding(self.out_template_pt.pt_render())
        output_html = compactify(output_html, filter_tags=False)
        return output_html

    def _exchange_relative_urls(self, output_html):
        """ exchange relative URLs and
            return dict with html, plain and images
        """
        parser_output_zpt = ENLHTMLParser(self)
        parser_output_zpt.feed(output_html)
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
        # don't use Header() with a str and a charset arg, even if it is correct
        # this would generate a encoded header and mail server may not support utf-8 encoded header
        from_header = Header(safe_unicode(sender_name))

        # get sender e-mail
        sender_email = request.get("sender_email", "")
        if sender_email == "":
            sender_email = enl.getSenderEmail()
        from_header.append('<%s>' % safe_unicode(sender_email))

        # get subject
        subject = request.get("subject", "")
        if subject == "":
            subject = self.Title()
        subject_header = Header(safe_unicode(subject))

        # Create from-header
        #from_header = enl.getSenderName() and '"%s" <%s>' % (sender_name, sender_email) or sender_email
        #from_header = safe_unicode(from_header)

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
        output_html = self._render_output_html()
        rendered_newsletter = self._exchange_relative_urls(output_html)
        text = rendered_newsletter['html']
        text_plain = rendered_newsletter['plain']
        image_urls = rendered_newsletter['images']
        props = getToolByName(self, "portal_properties").site_properties
        charset = props.getProperty("default_charset")

        for receiver in receivers:
            # create multipart mail
            outer = MIMEMultipart('alternative')

            if hasattr(request, "test"):
                outer['To'] = Header('<%s>' % safe_unicode(receiver['email']))

                fullname = receiver['fullname']
                salutation = receiver['salutation']
                personal_text = text.replace("[[SUBSCRIBER_SALUTATION]]", "")
                personal_text_plain = text_plain.replace("[[SUBSCRIBER_SALUTATION]]", "")
                personal_text = text.replace("[[UNSUBSCRIBE]]", "")
                personal_text_plain = text_plain.replace("[[UNSUBSCRIBE]]", "")
            else:
                if 'uid' in receiver:
                    try:
                        unsubscribe_text = enl.getUnsubscribe_string()
                    except AttributeError:
                        unsubscribe_text = "Click here to unsubscribe"
                    unsubscribe_link = enl.absolute_url() + "/unsubscribe?subscriber=" + receiver['uid']
                    personal_text = text.replace("[[UNSUBSCRIBE]]", """<a href="%s">%s.</a>""" % (unsubscribe_link, unsubscribe_text))
                    personal_text_plain = text_plain.replace("[[UNSUBSCRIBE]]", """\n%s: %s""" % (unsubscribe_text, unsubscribe_link))
                else:
                    personal_text = text.replace("[[UNSUBSCRIBE]]", "")
                    personal_text_plain = text_plain.replace("[[UNSUBSCRIBE]]", "")
                if 'salutation' in receiver:
                    salutation = receiver["salutation"]
                else:
                    salutation = ''
                fullname = receiver['fullname']
                if not fullname:
                    try:
                        fullname = enl.getFullname_fallback()
                    except AttributeError:
                        fullname = "Sir or Madam"
                outer['To'] = Header('<%s>' % safe_unicode(receiver['email']))

            subscriber_salutation = safe_portal_encoding(salutation) + ' ' + safe_portal_encoding(fullname)
            personal_text = personal_text.replace("[[SUBSCRIBER_SALUTATION]]", str(subscriber_salutation))
            personal_text_plain = personal_text_plain.replace("[[SUBSCRIBER_SALUTATION]]", str(subscriber_salutation))

            outer['From'] = from_header
            outer['Subject'] = subject_header
            outer.epilogue = ''

            # Attach text part
            #text_part = MIMEText(personal_text_plain, "plain", charset)

            # Attach html part with images
            #html_part =  MIMEText(personal_text, "html", charset)

            # Attach text part
            text_part = MIMEMultipart("related")
            text_part.attach(MIMEText(personal_text_plain, "plain", charset))

            # Attach html part with images
            html_part = MIMEMultipart("related")
            html_text = MIMEText(personal_text, "html", charset)
            html_part.attach(html_text)

            # Add images to the message
            image_number = 0
            reference_tool = getToolByName(self, 'reference_catalog')
            for image_url in image_urls:
                #XXX: we need to provide zope3 resource image too!
                try:
                    image_url = urlparse(image_url)[2]
                    if 'resolveuid' in image_url:
                        urlparts = image_url.split('/')[1:]
                        uuid = urlparts.pop(0)
                        o = reference_tool.lookupObject(uuid)
                        if o and urlparts:
                            # get thumb
                            o = o.restrictedTraverse(urlparts[0])
                    else:
                        o = self.restrictedTraverse(urllib.unquote(image_url))
                except Exception, e:
                    log.error("Could not resolve the image \"%s\": %s" % (image_url, e))
                else:
                    if hasattr(o, "_data"):                               # file-based
                        image = MIMEImage(o._data)
                    elif hasattr(o, "data"):
                        image = MIMEImage(o.data)                         # zodb-based
                    else:
                        image = MIMEImage(o.GET())                        # z3 resource image
                    image["Content-ID"] = "<image_%s>" % image_number
                    image_number += 1
                    # attach images only to html parts
                    html_part.attach(image)
            outer.attach(text_part)
            outer.attach(html_part)

            try:
                #MailHost.send(msg)
                MailHost.send(outer.as_string())
                log.info("Send newsletter to \"%s\"" % receiver['email'])
                send_counter += 1
            except AttributeError:  # Plone3.3.x
                MailHost.send(msg.as_string())
                log.info("Send newsletter to \"%s\"" % receiver['email'])
                send_counter += 1
            except Exception, e:
                log.info("Sending newsletter to \"%s\" failed, with error \"%s\"!" % (receiver['email'], e))
                send_error_counter += 1

        log.info("Newsletter was sent to (%s) receivers. (%s) errors occurred!" % (send_counter, send_error_counter))

        # change status only for a 'regular' send operation (not 'test', no
        # explicit recipients)
        if not hasattr(request, "test") and not recipients:
            wftool = getToolByName(self, "portal_workflow")
            if wftool.getInfoFor(self, 'review_state') == 'draft':
                wftool.doActionFor(self, "send")

    security.declareProtected("Modify portal content", "loadContent")
    def loadContent(self):
        """Loads text dependend on criteria into text attribute.
        """
        if self.getAcquireCriteria():
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
            log.info("SendToAllPloneMembers is true, so we add all existing members to receiver_member_list!")
            receiver_member_list = enl.get_plone_members()
            #if all members are receivers we don't need groups relations:
            receiver_group_list = []
        else:
            receiver_member_list = self.getPloneReceiverMembers()
            receiver_group_list = self.getPloneReceiverGroups()
        gtool = getToolByName(self, 'portal_groups')
        if fmp_tool:
            fmp_tool = queryUtility(IFastmemberpropertiesTool, 'fastmemberproperties_tool')
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

        # get salutation mappings
        salutation_mappings = {}
        for line in enl.getSalutations():
            salutation_key, salutation_value = line.split('|')
            salutation_mappings[salutation_key.strip()] = salutation_value.strip()
        # get all selected member properties
        for receiver_id in set(receiver_member_list):
            if receiver_id not in member_properties:
                log.debug("Ignore reveiver \"%s\", because we have no properties for this member!" % receiver_id)
                continue
            member_property = member_properties[receiver_id]
            if EMAIL_RE.findall(member_property['email']):
                plone_subscribers.append({
                    'fullname': member_property['fullname'],
                    'email': member_property['email'],
                    'salutation': salutation_mappings.get('default', ''),
                })
            else:
                log.debug("Skip '%s' because \"%s\" is not a real email!" % (receiver_id, member_property['email']))
        # run registered receivers post sending filter:
        for subscriber in subscribers([enl],
                                      IReceiversPostSendingFilter):
            plone_subscribers = subscriber.filter(plone_subscribers)
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
        anchorlist = "\n\n" + ("-" * plain_text_maxcols) + "\n\n"
        for item in parser.anchorlist:
            counter += 1
            anchorlist += "[%d] %s\n" % (counter, item)

        text = textout.getvalue() + anchorlist
        del textout, formtext, parser, anchorlist
        return text

    def getFiles(self):
        """ Return list of files in subtree """
        return self.getFolderContents(contentFilter=dict(portal_type=('File'),
                                      sort_on='getObjPositionInParent'))

atapi.registerType(ENLIssue, PROJECTNAME)
