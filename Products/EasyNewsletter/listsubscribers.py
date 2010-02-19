from zope.interface import implements

from interfaces import IListSubscribers

class ListSubscribers(object):
    """ Get the subscribers. This is a utility so you can implement your own
    harverster using a zcml override.
    """
    implements(IListSubscribers)

    def listSubscribers(self, context):
        """
        """
        return context.aq_inner.aq_parent.objectValues("ENLSubscriber")
