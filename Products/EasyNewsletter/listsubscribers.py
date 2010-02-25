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
        result = []
        parent_path = '/'.join(context.aq_inner.aq_parent.getPhysicalPath())
        found = context.portal_catalog(portal_type='ENLSubscriber',
                review_state='private',
                path={'query': parent_path})
        for sub in found:
            subscriber = sub.getObject()
            result += {'fullname': subscriber.getFullname(),
                       'email':    subscriber.getEmail(),
                       'UID':      subscriber.UID()},
        return result
