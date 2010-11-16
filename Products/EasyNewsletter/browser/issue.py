from BeautifulSoup import BeautifulSoup

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _

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
            putils.addPortalMessage(_("An error occured: %s") % e, "error")
        else:
            putils.addPortalMessage(_("The issue has been send."))

        return self.request.response.redirect(self.context.absolute_url())

    def get_public_body(self):
        """ Return the rendered HTML version (.body-text) 
            of the newsletter.
        """
        html = self.context._send_body()['html']
        soup = BeautifulSoup(html)
        return soup.find('div', {'class' : 'body-text'}).renderContents()
