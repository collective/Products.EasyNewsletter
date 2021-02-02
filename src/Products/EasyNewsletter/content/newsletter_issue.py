# -*- coding: utf-8 -*-
from .newsletter import get_content_aggregation_sources_base_path, INewsletter
from persistent.dict import PersistentDict
from plone import schema
from plone.app import textfield
from plone.app.z3cform.widget import SingleCheckBoxBoolFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.namedfile import field as namedfile
from plone.supermodel import model
from Products.EasyNewsletter import _
from z3c import relationfield
from zope.annotation.interfaces import IAnnotations
from zope.interface import implementer, Interface, provider
from zope.schema.interfaces import IContextAwareDefaultFactory


SEND_STATUS_KEY = 'PRODUCTS_EASYNEWSLETTER_SEND_STATUS'


@provider(IContextAwareDefaultFactory)
def get_default_output_template(parent):
    """ get ouput template from parent Newsletter
    """
    if INewsletter.providedBy(parent) and parent.__parent__:
        return parent.output_template


@provider(IContextAwareDefaultFactory)
def get_default_prologue(parent):
    """ get prologue from parent Newsletter
    """
    prologue_output = u""
    if INewsletter.providedBy(parent) and parent.__parent__ and parent.default_prologue:
        prologue_output = parent.default_prologue.raw
    default_prologue = textfield.RichTextValue(
        raw=prologue_output,
        mimeType="text/html",
        outputMimeType="text/x-plone-outputfilters-html",
    )
    return default_prologue


@provider(IContextAwareDefaultFactory)
def get_default_epilogue(parent):
    """ get epilogue from parent Newsletter
    """
    epilogue_output = u""
    if INewsletter.providedBy(parent) and parent.__parent__ and parent.default_epilogue:
        epilogue_output = parent.default_epilogue.raw
    default_epilogue = textfield.RichTextValue(
        raw=epilogue_output,
        mimeType="text/html",
        outputMimeType="text/x-plone-outputfilters-html",
    )
    return default_epilogue


@provider(IContextAwareDefaultFactory)
def get_default_content_aggregation_sources(parent):
    """ get content_aggregation_sources from parent Newsletter
    """
    if INewsletter.providedBy(parent) and parent.__parent__:
        return parent.content_aggregation_sources


class INewsletterIssue(model.Schema):
    """ Marker interface and Dexterity Python Schema for NewsletterIssue
    """

    model.fieldset(
        "customizations",
        label=_(u"Customizations"),
        fields=[
            "prologue",
            "epilogue",
            "content_aggregation_sources",
            "exclude_all_subscribers",
            "banner",
            "hide_image",
            "output_template",
        ],
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
        defaultFactory=get_default_content_aggregation_sources,
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
                {{subscriber_salutation}} and {{unsubscribe}} here.",
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
                {{subscriber_salutation}} and {{unsubscribe}} here.",
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

    # directives.order_after(content_aggregation_source="IBasic.title")
    # directives.order_after(output_template="IRichText.text")


def context_property(name):
    def getter(self):
        return getattr(self.context, name)

    def setter(self, value):
        setattr(self.context, name, value)

    def deleter(self):
        delattr(self.context, name)
    return property(getter, setter, deleter)


@implementer(INewsletterIssue)
class NewsletterIssue(Container):
    """
    """

    context_property('content_aggregation_sources')

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

    # XXX we should cache this call, it's called twice
    def get_image_src(self):
        """ find banner image, if not set on Issue we use the one from the Newsletter
        """
        img_src = ""
        if self.hide_image:
            return img_src
        scales = self.restrictedTraverse('@@images')
        if scales.scale('banner', scale='mini'):
            img_src = self.absolute_url() + "/@@images/banner"
            return img_src
        enl = self.get_newsletter()
        scales = enl.restrictedTraverse('@@images')
        if scales.scale('banner', scale='mini'):
            img_src = enl.absolute_url() + "/@@images/banner"
        return img_src

    def getHeader(self):
        if self.prologue:
            text = self.prologue.output
        else:
            text = u''
        return text

    def getFooter(self):
        if self.epilogue:
            text = self.epilogue.output
        else:
            text = u''
        return text

    def getText(self):
        if self.text:
            text = self.text.output
        else:
            text = u''
        return text

    # bbb: we should print a deprecation message here
    def getOutputTemplate(self):
        return self.output_template


class ISendStatus(Interface):
    """Manage send status for newsletter issues."""

    def clear():  # noqa: N805
        """Clear all records."""

    def add_records(records):  # noqa: N805
        """Add new records."""

    def get_records(status=None):  # noqa: N805
        """Return a list of all status information records."""

    def get_keys(status=None):  # noqa: N805
        """Return a list of all status information keys."""


@implementer(ISendStatus)
class SendStatus(object):
    def __init__(self, context):
        self.context = context

    def clear(self):
        """Clear all records."""
        annotations = IAnnotations(self.context)
        if SEND_STATUS_KEY in annotations:
            del annotations[SEND_STATUS_KEY]

    def add_records(self, records, key='email'):
        """Add new records."""
        annotations = IAnnotations(self.context)
        if SEND_STATUS_KEY not in annotations:
            annotations[SEND_STATUS_KEY] = PersistentDict()
        data = {data.get(key): data for data in records if data.get(key) is not None}
        annotations[SEND_STATUS_KEY].update(data)

    def get_records(self, successful=None):
        """Return a list of all status information records."""
        annotations = IAnnotations(self.context)
        if SEND_STATUS_KEY not in annotations:
            return []
        items = annotations[SEND_STATUS_KEY].values()
        if successful is not None:
            items = [
                item for item in items if
                item.get('status', {}).get('successful', None) == successful
            ]
        return items

    def get_keys(self, successful=None):
        """Return a list of all status information keys."""
        annotations = IAnnotations(self.context)
        if SEND_STATUS_KEY not in annotations:
            return []
        items = annotations[SEND_STATUS_KEY].items()
        if successful is not None:
            items = [
                key for key, item in items if
                item.get('status', {}).get('successful', None) == successful
            ]
        return items
