# -*- coding: utf-8 -*-
# from z3c.form.browser.radio import RadioFieldWidget
from plone import api, schema
from plone.app import textfield
from plone.app.z3cform.widget import SingleCheckBoxBoolFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.namedfile import field as namedfile
from plone.registry.interfaces import IRegistry
from plone.supermodel import model
from Products.EasyNewsletter import _, config
from z3c import relationfield
from zope.component import getUtility
from zope.interface import implementer


def get_default_output_template():
    registry = getUtility(IRegistry)
    templates_keys = list(registry.get("Products.EasyNewsletter.output_templates"))
    if not templates_keys:
        return
    if "output_default" not in templates_keys:
        default_tmpl_key = "output_default"
    else:
        default_tmpl_key = templates_keys[0]
    return default_tmpl_key


def _get_base_path(path):
    base_obj = api.content.get(path)
    if not base_obj:
        return
    base_path = "/".join(base_obj.getPhysicalPath())
    return base_path


def get_content_aggregation_sources_base_path(context):
    return _get_base_path("/")


class INewsletter(model.Schema):
    """ Marker interface and Dexterity Python Schema for Newsletter
    """

    # model.fieldset(
    #     'default',
    #     label=u'Default',
    #     fields=[
    #         'sender_email',
    #         'sender_name',
    #         'test_email',
    #         'content_aggregation_sources',
    #         'output_template',
    #     ],
    # )

    model.fieldset(
        "personalization",
        label=_(u"Personalization"),
        fields=[
            "salutations",
            "fullname_fallback",
            "unsubscribe_string",
            "subscriber_confirmation_mail_subject",
            "subscriber_confirmation_mail_text",
            "default_prologue",
            "default_epilogue",
            "banner",
            "logo",
        ],
    )

    model.fieldset(
        "recipients", label=_(u"Recipients"), fields=["exclude_all_subscribers"]
    )

    sender_email = schema.TextLine(
        title=_(u"ENL_label_senderEmail", default=u"Sender email"),
        description=_(
            u"ENL_help_senderEmail",
            default=u"Default for the sender address of the newsletters.",
        ),
        required=True,
    )

    sender_name = schema.TextLine(
        title=_(u"ENL_label_senderName", default=u"Sender name"),
        description=_(
            u"ENL_help_senderName",
            default=u"Default for the sender name of the newsletters.",
        ),
        required=True,
    )

    test_email = schema.TextLine(
        title=_(u"ENL_label_testEmail", default=u"Test email"),
        description=_(
            u"ENL_help_testEmail", default=u"Default for the test email address."
        ),
        required=True,
    )

    directives.widget(
        "content_aggregation_sources",
        pattern_options={
            "basePath": get_content_aggregation_sources_base_path,
            "selectableTypes": ["Collection"],
        },
    )
    content_aggregation_sources = relationfield.schema.RelationList(
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
            vocabulary="plone.app.vocabularies.Catalog",
        ),
        required=False,
    )

    salutations = schema.List(
        title=_(u"ENL_label_salutations", default=u"Subscriber Salutations."),
        description=_(
            u"ENL_help_salutations",
            default=u'Define here possible salutations for subscriber. \
                One salutation per line in the form of: "mr|Dear Mr.". \
                The left hand value "mr" or "ms" is mapped to salutation \
                of each subscriber and then the right hand value, which \
                you can customize is used as salutation.',
        ),
        default=[u"mr|Dear Mr.", u"ms|Dear Ms.", u"default|Dear"],
        value_type=schema.TextLine(title=u"salutation"),
        required=True,
    )

    fullname_fallback = schema.TextLine(
        title=_(
            u"ENL_label_fullname_fallback",
            default=u"Fallback for subscribers without a name.",
        ),
        description=_(
            u"ENL_help_fullname_fallback",
            default=u"This will be used if the subscriber has no fullname.",
        ),
        default=u"Sir or Madam",
        required=True,
    )

    unsubscribe_string = schema.TextLine(
        title=_(
            u"ENL_label_unsubscribe_string", default=u"Text for the 'unsubscribe' link"
        ),
        description=_(
            u"ENL_help_unsubscribe_string",
            default=u"This will replace the placeholder {{UNSUBSCRIBE}}.",
        ),
        default=u"Click here to unsubscribe",
        required=True,
    )

    # Make sure you import: plone.namedfile
    banner = namedfile.NamedBlobImage(
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
        title=_(u"ENL_label_default_header", default=u"Prologue"),
        description=_(
            u"ENL_description_text_header",
            default=u"The default prologue text. This is used as a default \
                for new issues. You can use placeholders like\
                {{subscriber_salutation}} and {{unsubscribe}} here.",
        ),
        default=_(u"{{subscriber_salutation}}<br />"),
        required=False,
    )

    # Make sure to import: plone.app.textfield
    default_epilogue = textfield.RichText(
        title=_(u"ENL_label_default_footer", default=u"Epilogue"),
        description=_(
            u"ENL_description_text_footer",
            default=u"The default epilogue text. This is used as a default \
                for new issues. You can use placeholders like\
                {{subscriber_salutation}} and {{unsubscribe}} here.",
        ),
        default=_(u"<h1>Community Newsletter for Plone</h1>\n{{unsubscribe}}"),
        required=False,
    )

    # Make sure you import:
    # plone.app.z3cform.widget.SingleCheckBoxBoolFieldWidget
    directives.widget(exclude_all_subscribers=SingleCheckBoxBoolFieldWidget)
    exclude_all_subscribers = schema.Bool(
        title=_(u"ENL_label_excludeAllSubscribers", default=u"Exclude all subscribers"),
        description=_(
            u"ENL_help_excludeAllSubscribers",
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
        vocabulary=u"Products.EasyNewsletter.OutputTemplates",
        defaultFactory=get_default_output_template,
        required=True,
    )

    subscriber_confirmation_mail_subject = schema.TextLine(
        title=_(
            u"ENL_label_subscriber_confirmation_mail_subject",
            default=u"Subscriber confirmation mail subject",
        ),
        description=_(
            u"ENL_description_subscriber_confirmation_mail_subject",
            default=u"Text used for confirmation email subject. You can \
                customize the text, but it should include the \
                placeholder: ${portal_url}!",
        ),
        default=config.DEFAULT_SUBSCRIBER_CONFIRMATION_MAIL_SUBJECT,
        required=True,
    )

    subscriber_confirmation_mail_text = schema.Text(
        title=_(
            u"ENL_label_subscriber_confirmation_mail_text",
            default=u"Subscriber confirmation mail text",
        ),
        description=_(
            u"ENL_description_subscriber_confirmation_mail_text",
            default=u"Text used for confirmation email. You can customize \
                the text, but it should include the placeholders: \
                ${portal_url}, ${subscriber_email} and \
                ${confirmation_url}!",
        ),
        default=config.DEFAULT_SUBSCRIBER_CONFIRMATION_MAIL_TEXT,
        required=True,
    )

    directives.order_after(content_aggregation_sources="IBasic.title")
    directives.order_after(test_email="IBasic.title")
    directives.order_after(sender_name="IBasic.title")
    directives.order_after(sender_email="IBasic.title")
    directives.order_after(output_template="IRichText.text")


@implementer(INewsletter)
class Newsletter(Container):
    """
    """

    def get_newsletter(self):
        return self

    # bbb to support ATCT way, needs to be removed in v5.x:
    getNewsletter = get_newsletter
