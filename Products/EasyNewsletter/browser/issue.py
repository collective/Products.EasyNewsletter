# Five imports
from Products.Five.browser import BrowserView

# CMFCore imports
from Products.CMFCore.utils import getToolByName

class IssueView(BrowserView):
    """
    """
    def refresh_issue(self):
        """
        """
        self.context.loadContent()
        self.request.response.redirect(self.context.absolute_url())

    def send_issue(self):
        """
        """
        putils = getToolByName(self.context, "plone_utils")
        try:
            self.context.send()
        except Exception, e:
            putils.addPortalMessage("An error occured: %s" % e, "error")
        else:
            putils.addPortalMessage("The issue has been send.")

        return self.request.response.redirect(self.context.absolute_url())