from Acquisition import aq_inner
# Five imports
from Products.Five.browser import BrowserView

# CMFCore imports
from Products.CMFCore.utils import getToolByName

from Products.EasyNewsletter import _

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
        context = aq_inner(self.context)
        putils = getToolByName(context, "plone_utils")
        wf_tool = getToolByName(context, "portal_workflow")
        try:
            wf_tool.doActionFor(context, 'send')
            context.send()
        except Exception:
            putils.addPortalMessage(_(u"error_occured", default="An error occured"), "error")
        else:
            putils.addPortalMessage(_(u"issue_send", default="The issue has been send."))

        return self.request.response.redirect(context.absolute_url())
