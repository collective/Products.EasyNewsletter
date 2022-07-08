# -*- coding: utf-8 -*-
# from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from bs4 import BeautifulSoup
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _  # noqa
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implementer


VALID_TAGS = [
    "strong",
    "b",
    "em",
    "p",
    "a",
    "ul",
    "ol",
    "li",
    "br",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
]


def sanitize_html(value):

    soup = BeautifulSoup(value)

    for tag in soup.findAll(True):
        if tag.name not in VALID_TAGS:
            tag.hidden = True

    return soup.renderContents()


class INewsletterSubscriberPortlet(IPortletDataProvider):
    """ """

    portlet_title = schema.TextLine(
        title=_("Title for the portlet."), default="Newsletter", required=True
    )

    portlet_description = schema.Text(
        title=_("label_subscriber_portlet_description", default="Description"),
        default="",
        required=False,
    )

    newsletter = schema.Choice(
        title=_("label_newsletter_path", default="Path to Newsletter"),
        description=_(
            "help_newsletter_path",
            default="Search for the accordingly newsletter, choose one and " "apply.",
        ),
        vocabulary="Products.EasyNewsletter.newsletters",
        required=True,
    )

    query_salutation = schema.Bool(
        title=_(
            "label_newletter_show_salutation",
            default="Ask for the salutation of the subscriber",
        ),
        default=True,
        required=False,
    )

    query_name = schema.Bool(
        title=_(
            "label_newletter_show_name", default="Ask for the name of the subscriber"
        ),
        default=True,
        required=False,
    )

    query_firstname = schema.Bool(
        title=_(
            "label_newletter_show_firstname", default="Ask for the firstname as well"
        ),
        default=False,
        required=False,
    )

    query_name_prefix = schema.Bool(
        title=_(
            "label_newletter_show_name_prefix",
            default="Ask for the name prefix (aka title) as well",
        ),
        default=False,
        required=False,
    )

    query_organization = schema.Bool(
        title=_(
            "label_newletter_show_organization",
            default="Display field to enter company/organization of " "subscriber",
        ),
        default=False,
        required=False,
    )

    show_unsubscribe = schema.Bool(
        title=_(
            "label_newletter_show_unsubscribe_link",
            default="Display an unsubscribe link in portlet footer",
        ),
        default=True,
        required=False,
    )

    additional_info = schema.Text(
        title=_(
            "label_subscriber_portlet_additional_info",
            default=(
                "Additional info, like terms and conditions.\n"
                "It can contain HTML, the following tags are allowed: {0}".format(
                    ", ".join(VALID_TAGS)
                )
            ),
        ),
        default="",
        required=False,
    )


@implementer(INewsletterSubscriberPortlet)
class Assignment(base.Assignment):
    """ """

    portlet_title = "Newsletter"
    portlet_description = ""
    newsletter = ""
    query_name = True
    query_firstname = False
    query_salutation = True
    query_name_prefix = False
    query_organization = False
    show_unsubscribe = True
    additional_info = ""

    def __init__(
        self,
        portlet_title="",
        portlet_description="",
        newsletter="",
        query_name=True,
        query_firstname=False,
        query_salutation=True,
        query_name_prefix=False,
        query_organization=False,
        show_unsubscribe=True,
        additional_info="",
    ):

        self.portlet_title = portlet_title
        self.portlet_description = portlet_description
        self.newsletter = newsletter
        self.query_name = query_name
        self.query_firstname = query_firstname
        self.query_salutation = query_salutation
        self.query_name_prefix = query_name_prefix
        self.query_organization = query_organization
        self.show_unsubscribe = show_unsubscribe
        self.additional_info = additional_info

    @property
    def title(self):
        """ """
        return _("Newsletter subscriber portlet")


class Renderer(base.Renderer):
    """ """

    render = ViewPageTemplateFile("subscriber.pt")

    @property
    def available(self):
        """ """
        return True

    def header(self):
        return self.data.portlet_title

    def description(self):
        return self.data.portlet_description

    def get_newsletter(self):
        """ """
        return self.data.newsletter

    def get_additional_info(self):
        return sanitize_html(self.data.additional_info)


class AddForm(base.AddForm):
    """ """

    schema = INewsletterSubscriberPortlet

    def create(self, data):
        """ """
        return Assignment(
            portlet_title=data.get("portlet_title", ""),
            portlet_description=data.get("portlet_description", ""),
            newsletter=data.get("newsletter", ""),
            query_name=data.get("query_name", ""),
            query_firstname=data.get("query_firstname", ""),
            query_salutation=data.get("query_salutation", ""),
            query_name_prefix=data.get("query_name_prefix", ""),
            query_organization=data.get("query_organization", ""),
            show_unsubscribe=data.get("show_unsubscribe", ""),
            additional_info=data.get("additional_info", ""),
        )


class EditForm(base.EditForm):
    """ """

    schema = INewsletterSubscriberPortlet
    label = _("Edit Newsletter portlet")
    description = _("This portlet displays the subscriber add form of a newsletter.")
