from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName


class IEnl_Subscribers_View(Interface):
    """
    Enl_Subscribers_View interface
    """

    def test():
        """ test method"""


class Enl_Subscribers_View(BrowserView):
    """
    Enl_Subscribers_View browser view
    """
    implements(IEnl_Subscribers_View)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def subscribers(self):
        results = self.portal_catalog(portal_type = 'ENLSubscriber', path='/'.join(self.context.getPhysicalPath()))
        return results
