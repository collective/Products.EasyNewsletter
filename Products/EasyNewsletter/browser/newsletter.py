from AccessControl.SecurityManagement import newSecurityManager

from Products.Five.browser import BrowserView

from Products.CMFCore.utils import getToolByName
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _

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
            putils.addPortalMessage(_("An error occured"), "error")
        else:
            newsletter = self.context
            # We do the deletion as the owner of the newsletter object
            # so that this is possible without login.
            owner = newsletter.getWrappedOwner()
            newSecurityManager(newsletter, owner)
            del newsletter[subscriber.id]
            putils.addPortalMessage(_("You have been unsubscribed."))

        return self.request.response.redirect(self.context.absolute_url())
