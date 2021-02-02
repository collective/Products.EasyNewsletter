# -*- coding: utf-8 -*-
from zope.interface import Attribute, Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IProductsEasyNewsletterLayer(IDefaultBrowserLayer):
    """
    """


class IIssueView(Interface):
    """
    """

    def get_unpersonalized_body(self):
        """
        """


class ISubscriberSource(Interface):
    """ Interface for utilities providing a list of subscribers.
        Such an utility should be registered as named utility since
        the name of the utility is referenced inside the Newsletter
        implementation as a reference to an external subscriber source.
    """

    def getSubscribers(newsletter):
        """ Return a list of subscribers for a given newsletter.
            Each subscriber should be represented as dictionary
            with keys 'email' and 'fullname'.
        """


class IReceiversMemberFilter(Interface):
    """ Marker interface for ReceiverMemberFilters subscribers.
        This filter runs befor the available member selections list is
        displayed, so you can use it to add or remove member entries
        from the selection list.
    """


class IReceiversGroupFilter(Interface):
    """ Marker interface for ReceiverGroupFilters subscribers.
        This filter runs befor the available group selections list is
        displayed, so you can use it to add or remove group entries for
        the selection list.
    """


class IReceiversPostSendingFilter(Interface):
    """ Marker interface for ReceiversPostSendingFilter subscribers.
        This filter runs after selection of members and groups, before
        sending. So this is the final line, to add or filter out
        recievers.
    """


class IENLRegistrationTool(Interface):
    """ Marker interface for ENL registration utility
    """


class IIssueDataFetcher(Interface):
    """ Provides personalized issue data
    """

    def __call__(receiver):
        """return issue data dict-like object with keys:

        ``subject_header``
            the subject header line

        - ``body_plain``
            the plain text body of the email

        - ``body_html``
            the html body of the email

        - ``images_to_attach``
            list of Image Plone content objects
        """

    def preview_html():
        """html meant for preview of the newsletter in browser.
        """


class IBeforePersonalizationEvent(Interface):

    data = Attribute("issue specific data")
