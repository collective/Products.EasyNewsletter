from zope.interface import Interface


class IEasyNewsletter(Interface):
    """
    """


class IENLIssue(Interface):
    """
    """


class IENLSubscriber(Interface):
    """
    """


class IENLTemplate(Interface):
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
