from zope import schema
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.EasyNewsletter import EasyNewsletterMessageFactory as _


class INewsletterSubscriberPortlet(IPortletDataProvider):
    """
    """
    portlet_title = schema.TextLine(
        title = _(u"Title for the portlet."),
        default = u"Newsletter",
        required = True,
    )

    portlet_description = schema.Text(
        title = _(u"label_newsletter_description",
            default=u"Description"),
        description = _(u"help_newsletter_description",
            default=u"Subscribe here to our newsletter."),
        default = u"",
        required = False)

    newsletter = schema.Choice(
        title = _(u"label_newsletter_title",
            default=u"Path to Newsletter"),
        description = _(u"help_newsletter_title",
            default=u"The absolute path from portal_root to the newsletter"),
        source = SearchableTextSourceBinder(
            {'portal_type': 'EasyNewsletter'},
            default_query='path:'),
        required=True)

    query_fullname = schema.Bool(
        title = _(u"label_newletter_show_fullname",
            default=u"Ask for the salutation and fullname of the subscriber"),
        default = True,
        required = True)

    query_organization = schema.Bool(
        title = _(
            u"label_newletter_show_organization",
            default=u"Display field to enter company/organization of subscriber"),
        default = False,
        required = True)


class Assignment(base.Assignment):
    """
    """
    implements(INewsletterSubscriberPortlet)

    portlet_title = "Newsletter"
    portlet_description = u""
    newsletter = u""
    query_fullname = True
    query_organization = False

    def __init__(self, portlet_title=u"", portlet_description=u"", newsletter="",
                 query_fullname = True, query_organization=False):
        """
        """
        self.portlet_title = portlet_title
        self.portlet_description = portlet_description
        self.newsletter = newsletter
        self.query_fullname = query_fullname
        self.query_organization = query_organization

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
            portlet_title = data.get("portlet_title", u""),
            portlet_description = data.get("portlet_description", u""),
            newsletter = data.get("newsletter", ""),
        )


class EditForm(base.EditForm):
    """
    """
    form_fields = form.Fields(INewsletterSubscriberPortlet)
    label = _(u"Edit Newsletter portlet")
    description = _(u"This portlet displays the subscriber add form of a newsletter.")
