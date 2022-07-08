# -*- coding: utf-8 -*-
# from z3c.form.browser.radio import RadioFieldWidget
from plone import api
from plone import schema
from plone.app import textfield
from plone.app.z3cform.widget import SingleCheckBoxBoolFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.namedfile import field as namedfile
from plone.registry.interfaces import IRegistry
from plone.supermodel import model
from Products.EasyNewsletter import _
from Products.EasyNewsletter import config
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
    """Marker interface and Dexterity Python Schema for Newsletter"""

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
        label=_("Personalization"),
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
        "recipients", label=_("Recipients"), fields=["exclude_all_subscribers"]
    )

    sender_email = schema.TextLine(
        title=_("ENL_label_senderEmail", default="Sender email"),
        description=_(
            "ENL_help_senderEmail",
            default="Default for the sender address of the newsletters.",
        ),
        required=True,
    )

    sender_name = schema.TextLine(
        title=_("ENL_label_senderName", default="Sender name"),
        description=_(
            "ENL_help_senderName",
            default="Default for the sender name of the newsletters.",
        ),
        required=True,
    )

    test_email = schema.TextLine(
        title=_("ENL_label_testEmail", default="Test email"),
        description=_(
            "ENL_help_testEmail", default="Default for the test email address."
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
            "ENL_content_aggregation_sources_label",
            default="Content aggregation sources",
        ),
        description=_(
            "ENL_content_aggregation_sources_desc",
            default="Choose sources to aggregate newsletter content from.",
        ),
        value_type=relationfield.schema.RelationChoice(
            title="content_aggretation_source",
            vocabulary="plone.app.vocabularies.Catalog",
        ),
        required=False,
    )

    salutations = schema.List(
        title=_("ENL_label_salutations", default="Subscriber Salutations."),
        description=_(
            "ENL_help_salutations",
            default='Define here possible salutations for subscriber. \
                One salutation per line in the form of: "mr|Dear Mr.". \
                The left hand value "mr" or "ms" is mapped to salutation \
                of each subscriber and then the right hand value, which \
                you can customize is used as salutation.',
        ),
        default=["mr|Dear Mr.", "ms|Dear Ms.", "default|Dear"],
        value_type=schema.TextLine(title="salutation"),
        required=True,
    )

    fullname_fallback = schema.TextLine(
        title=_(
            "ENL_label_fullname_fallback",
            default="Fallback for subscribers without a name.",
        ),
        description=_(
            "ENL_help_fullname_fallback",
            default="This will be used if the subscriber has no fullname.",
        ),
        default="Sir or Madam",
        required=True,
    )

    unsubscribe_string = schema.TextLine(
        title=_(
            "ENL_label_unsubscribe_string", default="Text for the 'unsubscribe' link"
        ),
        description=_(
            "ENL_help_unsubscribe_string",
            default="This will replace the placeholder {{UNSUBSCRIBE}}.",
        ),
        default="Click here to unsubscribe",
        required=True,
    )

    # Make sure you import: plone.namedfile
    banner = namedfile.NamedBlobImage(
        title=_("ENL_image_label", default="Banner image"),
        description=_(
            "ENL_image_desc",
            default="Banner image, you can include in the templates by"
            + "\n adding the {{banner}} placeholder into it."
            + " By default it should be 600x200 pixel.",
        ),
        required=False,
    )

    # Make sure you import: plone.namedfile
    logo = namedfile.NamedBlobImage(
        title=_("ENL_logo_label", default="Logo image"),
        description=_(
            "ENL_logo_desc",
            default="Logo image, you can include in the templates by\n"
            + " adding the {{logo}} placeholder into it.",
        ),
        required=False,
    )

    # Make sure to import: plone.app.textfield
    default_prologue = textfield.RichText(
        title=_("ENL_label_default_header", default="Prologue"),
        description=_(
            "ENL_description_text_header",
            default="The default prologue text. This is used as a default \
                for new issues. You can use placeholders like\
                {{subscriber_salutation}} and {{unsubscribe}} here.",
        ),
        default=_("{{subscriber_salutation}}<br />"),
        required=False,
    )

    # Make sure to import: plone.app.textfield
    default_epilogue = textfield.RichText(
        title=_("ENL_label_default_footer", default="Epilogue"),
        description=_(
            "ENL_description_text_footer",
            default="The default epilogue text. This is used as a default \
                for new issues. You can use placeholders like\
                {{subscriber_salutation}} and {{unsubscribe}} here.",
        ),
        default=_("<h1>Community Newsletter for Plone</h1>\n{{unsubscribe}}"),
        required=False,
    )

    # Make sure you import:
    # plone.app.z3cform.widget.SingleCheckBoxBoolFieldWidget
    directives.widget(exclude_all_subscribers=SingleCheckBoxBoolFieldWidget)
    exclude_all_subscribers = schema.Bool(
        title=_("ENL_label_excludeAllSubscribers", default="Exclude all subscribers"),
        description=_(
            "ENL_help_excludeAllSubscribers",
            default="If checked, the newsletter/mailing will not be send  \
                to all subscribers inside the newsletter. Changing this \
                setting does not affect already existing issues.",
        ),
        required=False,
        default=False,
    )

    output_template = schema.Choice(
        title=_("enl_label_output_template", default="Output template"),
        description=_(
            "enl_help_output_template",
            default="Choose the template to render the email. ",
        ),
        vocabulary="Products.EasyNewsletter.OutputTemplates",
        defaultFactory=get_default_output_template,
        required=True,
    )

    subscriber_confirmation_mail_subject = schema.TextLine(
        title=_(
            "ENL_label_subscriber_confirmation_mail_subject",
            default="Subscriber confirmation mail subject",
        ),
        description=_(
            "ENL_description_subscriber_confirmation_mail_subject",
            default="Text used for confirmation email subject. You can \
                customize the text, but it should include the \
                placeholder: ${portal_url}!",
        ),
        default=config.DEFAULT_SUBSCRIBER_CONFIRMATION_MAIL_SUBJECT,
        required=True,
    )

    subscriber_confirmation_mail_text = schema.Text(
        title=_(
            "ENL_label_subscriber_confirmation_mail_text",
            default="Subscriber confirmation mail text",
        ),
        description=_(
            "ENL_description_subscriber_confirmation_mail_text",
            default="Text used for confirmation email. You can customize \
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
    """ """

    def get_newsletter(self):
        return self

    # bbb to support ATCT way, needs to be removed in v5.x:
    getNewsletter = get_newsletter
