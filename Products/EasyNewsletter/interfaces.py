# zope imports
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

class IReceiversMemberFilter(Interface):
    """ Marker interface for ReceiverMemberFilters subscribers.
    """

class IReceiversGroupFilter(Interface):
    """ Marker interface for ReceiverGroupFilters subscribers.
    """

class IENLRegistrationTool(Interface):
    """ Marker interface for ENL registration utility
    """
