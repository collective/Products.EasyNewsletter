# -*- coding: utf-8 -*-
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.formlib import form
from zope.interface import implements


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
            default=u"Search for the accordingly newsletter, choose one and apply."),
        source=SearchableTextSourceBinder(
            {'portal_type': 'EasyNewsletter'},
            default_query='path:'),
        required=True)

    query_fullname = schema.Bool(
        title=_(
            u"label_newletter_show_fullname",
            default=u"Ask for the salutation and fullname of the subscriber"),
        default=True,
        required=True)

    query_firstname = schema.Bool(
        title=_(
            u"label_newletter_show_firstname",
            default=u"Ask for the firstname as well"),
        default=False,
        required=True)

    query_name_prefix = schema.Bool(
        title=_(
            u"label_newletter_show_name_prefix",
            default=u"Ask for the name prefix (aka title) as well"),
        default=False,
        required=True)

    query_organization = schema.Bool(
        title=_(
            u"label_newletter_show_organization",
            default=u"Display field to enter company/organization of "
            "subscriber"),
        default=False,
        required=True)

    show_unsubscribe = schema.Bool(
        title=_(
            u"label_newletter_show_unsubscribe_link",
            default=u"Display an unsubscribe link in portlet footer"),
        default=True,
        required=True)


class Assignment(base.Assignment):
    """
    """
    implements(INewsletterSubscriberPortlet)

    portlet_title = "Newsletter"
    portlet_description = u""
    newsletter = u""
    query_fullname = True
    query_firstname = False
    query_organization = False
    show_unsubscribe = True

    def __init__(
            self, portlet_title=u"", portlet_description=u"", newsletter="",
            query_fullname=True, query_firstname=True, query_organization=False,
            show_unsubscribe=True):

        self.portlet_title = portlet_title
        self.portlet_description = portlet_description
        self.newsletter = newsletter
        self.query_fullname = query_fullname
        self.query_firstname = query_firstname
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
    form_fields = form.Fields(INewsletterSubscriberPortlet)
    label = _(u"Edit Newsletter portlet")
    description = _(
        u"This portlet displays the subscriber add form of a newsletter.")
