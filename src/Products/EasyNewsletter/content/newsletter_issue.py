# -*- coding: utf-8 -*-
from .newsletter import get_content_aggregation_source_base_path
from .newsletter import INewsletter
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone import api
from plone import schema
from plone.app import vocabularies
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


class INewsletterIssue(model.Schema):
    """ Marker interface and Dexterity Python Schema for NewsletterIssue
    """

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
            source=vocabularies.catalog.CatalogSource(),
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


@implementer(INewsletterIssue)
class NewsletterIssue(Container):
    """
    """
