# -*- coding: utf-8 -*-
from .newsletter import get_content_aggregation_source_base_path
from .newsletter import INewsletter
from plone import api
from plone import schema
from plone.app import textfield
from plone.app import vocabularies as vocabs
from plone.app.vocabularies.catalog import CatalogSource
from plone.app.z3cform.widget import SingleCheckBoxBoolFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.namedfile import field as namedfile
from plone.supermodel import model
from Products.EasyNewsletter import _
from z3c import relationfield
from zope.interface import implementer
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory


@provider(IContextAwareDefaultFactory)
def get_default_output_template(context):
    """ get ouput template from parent Newsletter
    """
    if INewsletter.providedBy(context):
        return context.output_template


@provider(IContextAwareDefaultFactory)
def get_default_prologue(context):
    """ get prologue from parent Newsletter
    """
    if INewsletter.providedBy(context):
        return context.default_prologue


@provider(IContextAwareDefaultFactory)
def get_default_epilogue(context):
    """ get epilogue from parent Newsletter
    """
    if INewsletter.providedBy(context):
        return context.default_epilogue


class INewsletterIssue(model.Schema):
    """ Marker interface and Dexterity Python Schema for NewsletterIssue
    """

    model.fieldset(
        "customizations",
        label=_(u"Customizations"),
        fields=[
            "prologue",
            "epilogue",
            "content_aggregation_source",
            "exclude_all_subscribers",
            "image",
            "hide_image",
            "output_template",
        ],
    )

    directives.widget(
        "content_aggregation_source",
        pattern_options={
            "basePath": get_content_aggregation_source_base_path,
            "selectableTypes": ["Collection"],
        },
    )
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
            source=vocabs.catalog.CatalogSource(),
        ),
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

    # Make sure to import: plone.app.textfield
    prologue = textfield.RichText(
        title=_(u"ENL_label_default_header", default=u"Prologue"),
        description=_(
            u"ENL_description_text_header",
            default=u"The default prologue text. This is used as a default \
                for new issues. You can use placeholders like\
                {{SUBSCRIBER_SALUTATION}} and {{UNSUBSCRIBE}} here.",
        ),
        defaultFactory=get_default_prologue,
        required=False,
    )

    # Make sure to import: plone.app.textfield
    epilogue = textfield.RichText(
        title=_(u"ENL_label_default_footer", default=u"Epilogue"),
        description=_(
            u"ENL_description_text_footer",
            default=u"The default epilogue text. This is used as a default \
                for new issues. You can use placeholders like\
                {{SUBSCRIBER_SALUTATION}} and {{UNSUBSCRIBE}} here.",
        ),
        defaultFactory=get_default_epilogue,
        required=False,
    )

    # Make sure you import:
    # plone.app.z3cform.widget.SingleCheckBoxBoolFieldWidget
    directives.widget(hide_image=SingleCheckBoxBoolFieldWidget)
    hide_image = schema.Bool(
        title=_(u"label_issueHideImage", default=u"Hide banner image."),
        description=_(
            u"enl_issue_help_hide_image",
            default=u"If checked, the banner image defined on newsletter \
                    or on this issue will not be used.",
        ),
        required=False,
        default=False,
        readonly=False,
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

    # directives.order_after(content_aggregation_source="IBasic.title")
    # directives.order_after(output_template="IRichText.text")


@implementer(INewsletterIssue)
class NewsletterIssue(Container):
    """
    """

    def get_newsletter(self):
        return self.__parent__

    # bbb to support ATCT way, needs to be removed in v5.x:
    getNewsletter = get_newsletter

    def has_image(self):
        has_image = bool(self.get_image_src())
        return has_image

    def has_logo(self):
        enl = self.get_newsletter()
        has_logo = getattr(enl.aq_explicit, 'logo', None)
        return has_logo

    def get_image_src(self):
        img_src = ""
        if self.hide_image:
            return img_src
        scales = self.restrictedTraverse('@@images')
        if scales.scale('image', scale='mini'):
            img_src = self.absolute_url() + "/image"
            return img_src
        enl = self.get_newsletter()
        scales = enl.restrictedTraverse('@@images')
        if scales.scale('image', scale='mini'):
            img_src = enl.absolute_url() + "/image"
        return img_src

    # bbb: we should print a deprecation message here
    def getHeader(self):
        return self.prologue

    # bbb: we should print a deprecation message here
    def getFooter(self):
        return self.epilogue

    # bbb: we should print a deprecation message here
    def getOutputTemplate(self):
        return self.output_template