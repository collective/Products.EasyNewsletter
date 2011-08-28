from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

from Products.EasyNewsletter import EasyNewsletterMessageFactory as _
from Products.EasyNewsletter.config import PLACEHOLDERS


class IssueView(BrowserView):
    """
    """

    def refresh_issue(self):
        """Refresh the aggregate body when using collections.
        """
        if self.context.getAcquireCriteria():
            self.context.loadContent()
            self.request.response.redirect(self.context.absolute_url())

    def send_issue(self):
        """
        """
        putils = getToolByName(self.context, "plone_utils")
        self.context.send()
        putils.addPortalMessage(_("The issue has been send."))
        return self.request.response.redirect(self.context.absolute_url())

    def get_public_body(self):
        """ Return the rendered HTML version without placeholders.
        """
        html = self.context._render_output_html()
        for placeholder in PLACEHOLDERS:
            html = html.replace('[[' + placeholder + ']]', '')
        return html
