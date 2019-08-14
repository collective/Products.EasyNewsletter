# -*- coding: utf-8 -*-
# from plone.app.textfield import RichText
# from z3c.form.browser.radio import RadioFieldWidget
from plone import namedfile
from plone import schema
from plone.app import textfield
from plone.app import vocabularies
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from Products.EasyNewsletter import _
from z3c import relationfield
from zope.interface import implementer
from plone.app.z3cform.widget import SingleCheckBoxBoolFieldWidget


def get_default_output_template():
    pass


class INewsletter(model.Schema):
    """ Marker interface and Dexterity Python Schema for Newsletter
    """

    sender_email = schema.TextLine(
        title=_(u"EasyNewsletter_label_senderEmail", default=u"Sender email"),
        description=_(
            u"EasyNewsletter_help_senderEmail",
            default=u"Default for the sender address of the newsletters.",
        ),
        required=True,
    )

    sender_name = schema.TextLine(
        title=_(u"EasyNewsletter_label_senderName", default=u"Sender name"),
        description=_(
            u"EasyNewsletter_help_senderName",
            default=u"Default for the sender name of the newsletters.",
        ),
        required=True,
    )

    test_email = schema.TextLine(
        title=_(u"EasyNewsletter_label_testEmail", default=u"Test email"),
        description=_(
            u"EasyNewsletter_help_testEmail",
            default=u"Default for the test email address.",
        ),
        required=True,
    )

    # TODO: use selectable_types here
    # Make sure to import: z3c.relationfield and plone.app.vocabularies
    content_aggregation_source = relationfield.schema.RelationList(
        title=_(
            u"ENL_content_aggregation_sources_label",
            default=u"Content aggregation sources",
        ),
        description=_(
            u"ENL_content_aggregation_sources_desc",
            default=u"Choose sources to aggregate newsletter content from.",
        ),
        value_type=relationfield.schema.RelationChoice(
            title=u"content_aggretation_source",
            source=vocabularies.catalog.CatalogSource(portal_type="Collection"),
        ),
        required=False,
    )

    salutations = schema.List(
        title=_(
            u"EasyNewsletter_label_salutations", default=u"Subscriber Salutations."
        ),
        description=_(
            u"EasyNewsletter_help_salutations",
            default=u'Define here possible salutations for subscriber. \
                One salutation per line in the form of: "mr|Dear Mr.". \
                The left hand value "mr" or "ms" is mapped to salutation \
                of each subscriber and then the right hand value, which \
                you can customize is used as salutation.',
        ),
        value_type=schema.TextLine(title=u"salutation"),
        required=True,
    )

    fullname_fallback = schema.TextLine(
        title=_(
            u"EasyNewsletter_label_fullname_fallback",
            default=u"Fallback for subscribers without a name.",
        ),
        description=_(
            u"EasyNewsletter_help_fullname_fallback",
            default=u"This will be used if the subscriber has " "no fullname.",
        ),
        default=u"Sir or Madam",
        required=True,
    )

    unsubscribe_string = schema.TextLine(
        title=_(u"EasyNewsletter_label_unsubscribe_string"),
        description=_(u"EasyNewsletter_help_unsubscribe_string"),
        default=_(
            u"EasyNewsletter_default_unsubscribe_string",
            default=u"Click here to unsubscribe",
        ),
        required=True,
    )

    # Make sure you import: plone.namedfile
    image = namedfile.NamedBlobImage(
        title=_(u"ENL_image_label", default=u"Banner image"),
        description=_(
            u"ENL_image_desc",
            default=u"Banner image, you can include in the templates by"
            + u"\n adding the {{banner}} placeholder into it."
            + u" By default it should be 600x200 pixel.",
        ),
        required=False,
    )

    # Make sure you import: plone.namedfile
    logo = namedfile.NamedBlobImage(
        title=_(u"ENL_logo_label", default=u"Logo image"),
        description=_(
            u"ENL_logo_desc",
            default=u"Logo image, you can include in the templates by\n"
            + u" adding the {{logo}} placeholder into it.",
        ),
        required=False,
    )

    # Make sure to import: plone.app.textfield
    default_prologue = textfield.RichText(
        title=_(u"EasyNewsletter_label_default_header", default=u"Prologue"),
        description=_(
            u"description_text_header",
            default=u"The default prologue text. This is used as a default \
                for new issues. You can use placeholders like\
                {{SUBSCRIBER_SALUTATION}} and {{UNSUBSCRIBE}} here.",
        ),
        default=_(u"{{SUBSCRIBER_SALUTATION}}<br />"),
        required=False,
    )

    # Make sure to import: plone.app.textfield
    default_epilogue = textfield.RichText(
        title=_(u"EasyNewsletter_label_default_footer", default=u"Epilogue"),
        description=_(
            u"description_text_footer",
            default=u"The default epilogue text. This is used as a default \
                for new issues. You can use placeholders like\
                {{SUBSCRIBER_SALUTATION}} and {{UNSUBSCRIBE}} here.",
        ),
        default=_(u"<h1>Community Newsletter for Plone</h1>\n{{UNSUBSCRIBE}}"),
        required=False,
    )

    # Make sure you import:
    # plone.app.z3cform.widget.SingleCheckBoxBoolFieldWidget
    directives.widget(exclude_all_subscribers=SingleCheckBoxBoolFieldWidget)
    exclude_all_subscribers = schema.Bool(
        title=_(u"label_excludeAllSubscribers", default=u"Exclude all subscribers"),
        description=_(
            u"help_excludeAllSubscribers",
            default=u"If checked, the newsletter/mailing will not be send  \
                to all subscribers inside the newsletter. Changing this \
                setting does not affect already existing issues.",
        ),
        required=False,
        default=False,
    )

    output_template = schema.Choice(
        title=_(u"enl_label_output_template", default="Output template"),
        description=_(
            u"enl_help_output_template",
            default=u"Choose the template to render the email. ",
        ),
        vocabulary=u"Products.EasyNewsletter.output_templates",
        defaultFactory=get_default_output_template,
        required=True,
    )


@implementer(INewsletter)
class Newsletter(Container):
    """
    """
