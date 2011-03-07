import csv
import re
import tempfile

from types import DictType

from Acquisition import aq_inner, aq_parent

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

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def create_subscribers(self, csv_data=None):
        """Create newsletter subscribers from uploaded CSV file.
        """
        
        # Do nothing if no submit button was hit
        if 'form.button.Import' not in self.request.form:
            return
        
        context = aq_inner(self.context)
        plone_utils = getToolByName(self.context, 'plone_utils')
        encoding = plone_utils.getSiteEncoding()
        existing = self.context.objectIds()
        messages = IStatusMessage(self.request)
        success = []
        fail = []
        data = []

        # Show error if no file was specified
        filename = self.request.form.get('csv_upload', None)
        if not filename:
            msg = _('No file specified.')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return self.request.response.redirect(context.absolute_url() + '/@@upload_csv')

        # Show error if no data has been provided in the file
        reader = csv.reader(filename)
        header = reader.next()
        if header != CSV_HEADER:
            msg = _('Wrong specification of the CSV file. Please correct it and retry.')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return self.request.response.redirect(context.absolute_url() + '/@@upload_csv')

        for subscriber in reader:
            # Check the length of the line
            if len(subscriber) != 4:
                fail.append(
                    {'failure': 'The number of items in the line is not correct. It should be 4. Check your CSV file.'})
            else:
                salutation = subscriber[0]
                fullname = subscriber[1]
                email = subscriber[2]
                organization = subscriber[3]
                id = plone_utils.normalizeString(email)
                if id in existing:
                    fail.append(
                        {'salutation': salutation,
                         'fullname': fullname,
                         'email': email,
                         'organization': organization,
                         'failure': 'This email address is already registered.'})
                else:
                    title = email + " - " + fullname
                    try:
                        self.context.invokeFactory('ENLSubscriber',
                            id=id, 
                            title=title, 
                            description="")
                        sub = context[id]
                        sub.email = email
                        sub.fullname = fullname.decode(encoding)
                        sub.organization = organization.decode(encoding)
                        sub.salutation = salutation.decode(encoding)
                        obj = self.context.get(id, None)
                        obj.reindexObject()
                        success.append(
                                {'salutation': salutation,
                                 'fullname': fullname,
                                 'email': email,
                                 'organization': organization})
                    except Exception, e:
                        fail.append(
                            {'salutation': salutation,
                             'fullname': fullname,
                             'email': email,
                             'organization': organization,
                             'failure': 'An error occured while creating this subscriber: %s' % str(e)})

        return {'success' : success, 'fail' : fail}


class DownloadCSV(BrowserView):
         
    def __call__(self):
        """Returns a CSV file with all newsletter subscribers.
        """
        context = aq_inner(self.context)
        ctool = getToolByName(context, 'portal_catalog')

        # Create CSV file
        filename = tempfile.mktemp()
        file = open(filename, 'wb')
        csvWriter = csv.writer(file, 
                               delimiter=',',
                               quotechar='"', 
                               quoting=csv.QUOTE_MINIMAL)
        csvWriter.writerow(CSV_HEADER)
        for subscriber in ctool(portal_type = 'ENLSubscriber',
                                path='/'.join(self.context.getPhysicalPath()),
                                sort_on='email'): 
            obj = subscriber.getObject()
            csvWriter.writerow([
                obj.salutation.encode("utf-8"),
                obj.fullname.encode("utf-8"),
                obj.email,
                obj.organization.encode("utf-8")])
        file.close()
        data = open(filename, "r").read()
        
        # Create response
        response = context.REQUEST.response
        response.addHeader('Content-Disposition', "attachment; filename=easynewsletter-subscribers.csv")
        response.addHeader('Content-Type', 'text/csv')
        response.addHeader('Content-Length', "%d" % len(data))
        response.addHeader('Pragma', "no-cache")
        response.addHeader('Cache-Control', "must-revalidate, post-check=0, pre-check=0, public")
        response.addHeader('Expires', "0")
        
        # Return CSV data
        return data
    