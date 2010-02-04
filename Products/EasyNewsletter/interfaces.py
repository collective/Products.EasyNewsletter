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
