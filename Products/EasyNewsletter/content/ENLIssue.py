# python imports
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEImage import MIMEImage

# zope imports
from zope.interface import implements
from zope.component import getUtility 

# Zope / Plone import
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.ATContentTypes import ATCTMessageFactory as _
from Products.ATContentTypes.content.topic import ATTopic
from Products.ATContentTypes.content.topic import ATTopicSchema
from Products.CMFCore.utils import getToolByName

# EasyNewsletter imports
from Products.EasyNewsletter.interfaces import IENLIssue, IListSubscribers
from Products.EasyNewsletter.config import PROJECTNAME
from Products.EasyNewsletter.utils.ENLHTMLParser import ENLHTMLParser

schema=Schema((

    TextField('header',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword',),
        widget=RichWidget(
            rows=20,
            label='Header',
            label_msgid='EasyNewsletter_label_header',
            description_msgid='EasyNewsletter_help_header',
            i18n_domain='EasyNewsletter',
        ),
        default_output_type = 'text/x-html-enl',
    ),

    TextField('text',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword',),
        widget=RichWidget(
            rows=30,
            label='Text',
            label_msgid='EasyNewsletter_label_text',
            description_msgid='EasyNewsletter_help_text',
            i18n_domain='EasyNewsletter',
        ),
        default_output_type = 'text/x-html-enl',
    ),

    TextField('footer',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword',),
        widget=RichWidget(
            rows=20,
            label='Footer',
            label_msgid='EasyNewsletter_label_footer',
            description_msgid='EasyNewsletter_help_footer',
            i18n_domain='EasyNewsletter',
        ),
        default_output_type = 'text/x-html-enl',
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
        default="default",
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

    #LinesField('ploneMembersAndGroups',
    #    vocabulary="nested_users_and_groups",
    #    widget=MultiSelectionWidget(
    #        label='Plone Members and Groups',
    #        label_msgid='EasyNewsletter_label_ploneMembersAndGroups',
    #        description_msgid='EasyNewsletter_help_ploneMembersAndGroups',
    #        i18n_domain='EasyNewsletter',
    #    )
    #),
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
        """Overwritten to "forbid"" folder_contents
        """
        url = self.absolute_url()
        self.REQUEST.RESPONSE.redirect(url)

    security.declarePublic('send')
    def send(self):
        """Sends the newsletter
        """
        # preparations
        request = self.REQUEST
        enl = self.aq_inner.aq_parent

        # get sender name
        sender_name = request.get("sender_name", "")
        if sender_name == "":
            sender_name = enl.getSenderName()

        # get sender e-mail
        sender_email = request.get("sender_email", "")
        if sender_email == "":
            sender_email = enl.getSenderEmail()

        # get test e-mail
        test_receiver = request.get("test_receiver", "")
        if test_receiver == "":
            test_receiver = enl.getTestEmail()

        # get subject
        subject = request.get("subject", "")
        if subject == "":
            subject = self.Title()

        # Create from-header
        if sender_name:
            from_header = "%s <%s>" % (sender_name, sender_email)
        else:
            from_header = sender_email

        if hasattr(request, "test"):
            receivers = [test_receiver]
        else:
            listSubscribers = getUtility(IListSubscribers)
            receivers = listSubscribers.listSubscribers(self)

        # get charset
        props = getToolByName(self, "portal_properties").site_properties
        charset = props.getProperty("default_charset")

        # exchange relative URLs
        parser = ENLHTMLParser(self, cid_images=True)
        parser.feed(self.getText())
        text = parser.html

        # create & attach text part
        text_plain = self.portal_transforms.convert('html_to_text', text).getData()

        for receiver in receivers:
            # create multipart mail
            mail = MIMEMultipart("alternative")
            personal_text = text
            personal_text_plain = text_plain

            if hasattr(request, "test"):
                mail['To'] = receiver
            else:
                # remove ::PERSOLINE:: Maker first:
                personal_text = personal_text.replace("::PERSOLINE::", "")
                personal_text_plain = personal_text_plain.replace("::PERSOLINE::", "")
                unsubscribe_link = enl.absolute_url() + "/unsubscribe?subscriber=" + receiver['UID']
                personal_text = personal_text.replace("{% unsubscribe-link %}", unsubscribe_link)
                personal_text_plain = personal_text_plain.replace("{% unsubscribe-link %}", unsubscribe_link)
                fullname = None
                fullname = receiver['fullname']
                if not fullname:
                    fullname = "Sir or Madam"
                personal_text = personal_text.replace("{% subscriber-fullname %}", fullname)
                personal_text_plain = personal_text_plain.replace("{% subscriber-fullname %}", fullname)
                mail['To'] = receiver['email']

            mail['From']    = from_header
            mail['Subject'] = subject
            mail.epilogue   = ''

            # Attach text part
            text_part = MIMEText(personal_text_plain, "plain", charset)
            mail.attach(text_part)

            # Attach html part with images
            html_part = MIMEMultipart("related")
            # Setting the Content-Transfer-Encoding fixes error with MailHost
            html_part['Content-Transfer-Encoding'] = 'quoted-printable'

            html_text = MIMEText(personal_text, "html", charset)
            html_part.attach(html_text)

            # Add images to the message
            image_number = 0
            for o in parser.image_objs:
                if hasattr(o, "_data"):                               # file-based
                    image = MIMEImage(o._data)
                else:
                    image = MIMEImage(o.data)                         # zodb-based
                image["Content-ID"] = "image_%s" % image_number
                image_number += 1
                html_part.attach(image)

            mail.attach(html_part)
            self.MailHost.send(mail.as_string())

        # change status
        if not hasattr(request, "test"):
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
        unpersonalized_body = '\r\n'.join([line for line in personalized_body_lines if not "::PERSOLINE::" in line])

        parser = ENLHTMLParser(self)
        parser.feed(unpersonalized_body)

        return parser.html


    #def get_members(self):
    #    """
    #    """
    #    mtool = getToolByName(self, 'portal_membership')
    #    members = mtool.listMemberIds()
    #    return DisplayList()

    #def get_group_members():
    #    """
    #    """
    #    mtool = getToolByName(self, 'portal_membership')
    #    gtool = getToolByName(self, 'portal_groups')
    #    members = mtool.listMemberIds()
    #    groups = gtool.listGroups()
    #    for group in groups:
    #        group_members[group.id] = group.getGroupMemberIds()
    #    return DisplayList()


registerType(ENLIssue, PROJECTNAME)
