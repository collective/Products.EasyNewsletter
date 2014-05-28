from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView


class NewsletterView(BrowserView):
    """
    """

    def getRenderedIssues(self):
        """ Return the rendered body of all newsletter issues """

        result = list()
        catalog = getToolByName(self.context, "portal_catalog")
        for brain in catalog(portal_type='ENLIssue',
                             path='/'.join(self.context.getPhysicalPath())):
            issue = brain.getObject()
            content = issue.restrictedTraverse('@@get-public-body')()
            result.append(dict(content=content, title=issue.Title()))
        return result
