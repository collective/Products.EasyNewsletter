from zope.interface import implements, Interface
from zope import schema
from zope.app.component.hooks import getSite

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _


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
        results = self.portal_catalog(portal_type = 'ENLSubscriber', path='/'.join(self.context.getPhysicalPath()), sort_on='email')
        return results


class UploadCSV(BrowserView):
    """ TODO: build a reald upload-form for cvs-files.
        creates subscribers from csv-data
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def read_file(self):
        csv_data = [("Testum Testing", "tester1@mydomain.de"), ("Tester2", "tester2@mydomain.de"),("Tester3", "tester3@mydomain.de")]
        return csv_data

    def read_data(self):
        """ Here you can enter your user. By calling www.mysite.com/mynewsletter/@@upload_csv
            you can import these into your newsletter.
        """
        data = [("Dummy Name", "dummy@email.com", "Dummy Company"),
                ("Another Dummy", "dummy2@email.com", "United Nations")]
        return data

    def create_subscribers(self, csv_data):
        self.portal.plone_log("Creating subscribers")
        plone_utils = getToolByName(self.context, 'plone_utils')
        existing = self.context.objectIds()
        messages = IStatusMessage(self.request)
        success = []
        fail = []
        for new_subscriber in self.read_data():
            email = new_subscriber[1]
            id = plone_utils.normalizeString(email)
            if id in existing:
                messages.addStatusMessage(_("Your e-mail address is already registered."), "error")
                fail.append(email)
            else:
                fullname = new_subscriber[0]
                organization = new_subscriber[2]
                title = email + " - " + fullname
                self.context.invokeFactory('ENLSubscriber', id=id, title=title, description="", email=email, fullname=fullname, organization=organization)
                obj = self.context.get(id, None)
                obj.reindexObject()
                success.append(email)
        return {'success' : success, 'fail' : fail}
        
        