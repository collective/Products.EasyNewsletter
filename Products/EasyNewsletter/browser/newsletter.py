# Five imports
from Products.Five.browser import BrowserView

# CMFCore imports
from Products.CMFCore.utils import getToolByName

class NewsletterView(BrowserView):
    """
    """
    def unsubscribe(self):
        """
        """
        putils = getToolByName(self.context, "plone_utils")
        catalog = getToolByName(self.context, "portal_catalog")

        try:
            subscriber = catalog.searchResults(UID = self.request.get("subscriber", ""))[0]
        except IndexError:
            putils.addPortalMessage("An error occured", "error")
        else:
            newsletter = self.context
            del newsletter[subscriber.id]
            putils.addPortalMessage("You have been unsubscribed.")

        return self.request.response.redirect(self.context.absolute_url())