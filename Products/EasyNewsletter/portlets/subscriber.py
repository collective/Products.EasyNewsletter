# zope imports
from zope import schema
from zope.formlib import form
from zope.interface import implements

# plone imports
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

# Five imports
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView

class INewsletterSubscriberPortlet(IPortletDataProvider):
    """
    """
    portlet_title = schema.TextLine(
        title = _(u"Title for the portlet."),
        default = u"Newsletter",
        required = True,
    )

    portlet_description = schema.Text(
            title=_(u"label_newsletter_description", default=u"Description"),
            description=_(u"help_newsletter_description",
                          default=u"Subscribe here to our newsletter."),
            default=u"",
            required=False)

    newsletter = schema.TextLine(
            title=_(u"label_newsletter_title", default=u"Path to Newsletter"),
            description=_(u"help_newsletter_title",
                          default=u"The absolute path from portal_root to the newsletter"),
            default=u"",
            required=True)


class Assignment(base.Assignment):
    """
    """
    implements(INewsletterSubscriberPortlet)

    def __init__(self, portlet_title="", portlet_description="", newsletter=""):
        """
        """
        self.portlet_title = portlet_title
        self.portlet_description = portlet_description
        self.newsletter = newsletter

    @property
    def title(self):
        """
        """
        return _(u"Newsletter Subscriber")

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
            portlet_title = data.get("portlet_title", ""),
            portlet_description = data.get("portlet_description", ""),
            newsletter = data.get("newsletter", ""),
        )

class EditForm(base.EditForm):
    """
    """
    form_fields = form.Fields(INewsletterSubscriberPortlet)
    label = _(u"Edit Newsletter portlet")
    description = _(u"This portlet displays the subscriber add form of a newsletter.")


class SubscriberView(BrowserView):
    """
    """
    def add_subscriber(self):
        """
        """
        putils = getToolByName(self.context, "plone_utils")
        portal_url = getToolByName(self.context, "portal_url")
        path_to_easynewsletter = self.request.get("newsletter")

        # remove leading slash from paths like: /mynewsletter
        path_to_easynewsletter = path_to_easynewsletter.strip('/')

        MESSAGE_CODE = [
            "Your e-mail has been added. Thanks for your interest.",
            "Please enter a valid e-mail address.",
            "Your e-mail address is already registered."
            ]
        
        subscriber = self.request.get("subscriber", "")
        fullname = self.request.get("fullname", "")
        easynewsletter = portal_url.restrictedTraverse(path_to_easynewsletter)
        valid_email, error_code = easynewsletter.addSubscriber(subscriber, fullname)

        if valid_email == True:
            putils.addPortalMessage(MESSAGE_CODE[0])
        else:
            putils.addPortalMessage(MESSAGE_CODE[error_code], "error")

        self.request.response.redirect(self.context.absolute_url())
