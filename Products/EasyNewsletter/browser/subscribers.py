from zope.interface import implements, Interface
from zope import schema
from zope.component import getUtility
from zope.app.component.hooks import getSite

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _
from Products.EasyNewsletter.config import SALUTATION
from Products.EasyNewsletter.interfaces import ISubscriberSource
import csv
import re

regex = r"^[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)*[a-zA-Z]{2,4}$"
check_email = re.compile(regex).match
def validate_email(value):
    if not check_email(value):
        return False
    return True

CSV_HEADER = [
    'salutation',              
    'fullname',
    'email',
    'organization',
]



class IEnl_Subscribers_View(Interface):
    """
    Enl_Subscribers_View interface
    """

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
        subscribers = list()

        # Plone subscribers
        for brain in self.portal_catalog(portal_type = 'ENLSubscriber',
                                         path='/'.join(self.context.getPhysicalPath()),
                                         sort_on='email'):
            if brain.salutation:
                salutation = SALUTATION.getValue(brain.salutation, '')
            else:
                salutation = ''
            subscribers.append(dict(source='plone',
                               deletable=True,
                               email=brain.email,
                               getURL=brain.getURL(),
                               salutation=salutation,
                               fullname=brain.fullname,
                               organization=brain.organization))

        # External subscribers
        external_source_name = self.context.getSubscriberSource()
        if external_source_name != 'default':
            try:
                external_source = getUtility(ISubscriberSource, name=external_source_name)
            except ComponentLookupError:
                pass

            for subscriber in external_source.getSubscribers(self.context):
                subscriber['source'] = external_source_name
                subscribers.append(subscriber)

        return subscribers


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
        data = []
        file_upload = self.request.form.get('csv_upload', None)
        if file_upload is None or not file_upload.filename:
            return data
        #data = [("Dummy Name", "dummy@email.com", "Dummy Company"),
        #        ("Another Dummy", "dummy2@email.com", "United Nations")]

        reader = csv.reader(file_upload)
        header = reader.next()
        if header != CSV_HEADER:
            msg = _('Wrong specification of the CSV file. Please correct it and retry.')
            type = 'error'
            IStatusMessage(self.request).addStatusMessage(msg, type=type)
            return data
        for row in reader:
            data.append(row)
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
            elif not(validate_email(email)):
                messages.addStatusMessage(_("Invalid e-mail address."), "error")
                fail.append(email)
            else:
                fullname = new_subscriber[0]
                organization = new_subscriber[2]
                title = email + " - " + fullname
                try:
                    self.context.invokeFactory('ENLSubscriber',
                        id=id, title=title, description="", email=email,
                        fullname=fullname, organization=organization)
                except:
                    messages.addStatusMessage(_("Error creating subscriber."), "error")
                    fail.append(email)
                obj = self.context.get(id, None)
                obj.reindexObject()
                success.append(email)
        return {'success' : success, 'fail' : fail}


