# -*- coding: utf-8 -*-
from plone.app.portlets.portlets import base
# from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.portlets.interfaces import IPortletDataProvider
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _  # noqa
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implements
from Products.EasyNewsletter.config import IS_PLONE_5


if not IS_PLONE_5:  # BBB
    from zope.formlib import form


class INewsletterSubscriberPortlet(IPortletDataProvider):
    """
    """
    portlet_title = schema.TextLine(
        title=_(u"Title for the portlet."),
        default=u"Newsletter",
        required=True,
    )

    portlet_description = schema.Text(
        title=_(
            u"label_subscriber_portlet_description",
            default=u"Description"),
        default=u"",
        required=False)

    newsletter = schema.Choice(
        title=_(
            u"label_newsletter_path",
            default=u"Path to Newsletter"),
        description=_(
            u"help_newsletter_path",
            default=u"Search for the accordingly newsletter, choose one and "
                    u"apply."
        ),
        vocabulary="Products.EasyNewsletter.newsletters",
        required=True)

    query_salutation = schema.Bool(
        title=_(
            u"label_newletter_show_salutation",
            default=u"Ask for the salutation of the subscriber"),
        default=True,
        required=False)

    query_name = schema.Bool(
        title=_(
            u"label_newletter_show_name",
            default=u"Ask for the name of the subscriber"),
        default=True,
        required=False)

    query_firstname = schema.Bool(
        title=_(
            u"label_newletter_show_firstname",
            default=u"Ask for the firstname as well"),
        default=False,
        required=False)

    query_name_prefix = schema.Bool(
        title=_(
            u"label_newletter_show_name_prefix",
            default=u"Ask for the name prefix (aka title) as well"),
        default=False,
        required=False)

    query_organization = schema.Bool(
        title=_(
            u"label_newletter_show_organization",
            default=u"Display field to enter company/organization of "
            "subscriber"),
        default=False,
        required=False)

    show_unsubscribe = schema.Bool(
        title=_(
            u"label_newletter_show_unsubscribe_link",
            default=u"Display an unsubscribe link in portlet footer"),
        default=True,
        required=False)


class Assignment(base.Assignment):
    """
    """
    implements(INewsletterSubscriberPortlet)

    portlet_title = "Newsletter"
    portlet_description = u""
    newsletter = u""
    query_name = True
    query_firstname = False
    query_salutation = True
    query_name_prefix = False
    query_organization = False
    show_unsubscribe = True

    def __init__(
            self, portlet_title=u"", portlet_description=u"", newsletter="",
            query_name=True, query_firstname=False,
            query_salutation=True, query_name_prefix=False,
            query_organization=False, show_unsubscribe=True):

        self.portlet_title = portlet_title
        self.portlet_description = portlet_description
        self.newsletter = newsletter
        self.query_name = query_name
        self.query_firstname = query_firstname
        self.query_salutation = query_salutation
        self.query_name_prefix = query_name_prefix
        self.query_organization = query_organization
        self.show_unsubscribe = show_unsubscribe

    @property
    def title(self):
        """
        """
        return _(u"Newsletter subscriber portlet")


class Renderer(base.Renderer):
    """
    """
    render = ViewPageTemplateFile('subscriber.pt')

    @property
    def available(self):
        """
        """
        return True

    def header(self):
        return self.data.portlet_title

    def description(self):
        return self.data.portlet_description

    def get_newsletter(self):
        """
        """
        return self.data.newsletter


class AddForm(base.AddForm):
    """
    """
    if IS_PLONE_5:
        schema = INewsletterSubscriberPortlet
    else:  # BBB
        form_fields = form.Fields(INewsletterSubscriberPortlet)

    def create(self, data):
        """
        """
        return Assignment(
            portlet_title=data.get("portlet_title", u""),
            portlet_description=data.get("portlet_description", u""),
            newsletter=data.get("newsletter", ""),
        )


class EditForm(base.EditForm):
    """
    """
    if IS_PLONE_5:
        schema = INewsletterSubscriberPortlet
    else:  # BBB
        form_fields = form.Fields(INewsletterSubscriberPortlet)

    label = _(u"Edit Newsletter portlet")
    description = _(
        u"This portlet displays the subscriber add form of a newsletter.")
