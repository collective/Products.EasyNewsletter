from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName


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
        results = self.portal_catalog(portal_type = 'ENLSubscriber', path='/'.join(self.context.getPhysicalPath()))
        return results


#
#from plone.z3cform.crud import crud
#import cStringIO
#import csv
#
#def parseSubscriberCSVFile(subscriberdata, composer,
#                           header_row_present=False,
#                           delimiter=csv_delimiter):
#    """parses file containing subscriber data
#
#    returns list of dictionaries with subscriber data according to composer"""
#    properties = component.getUtility(IPropertiesTool)
#    charset = properties.site_properties.getProperty('default_charset',
#                                                     'utf-8').upper()
#    try:
#        data = cStringIO.StringIO(subscriberdata)
#        reader = csv.reader(data, delimiter=str(delimiter))
#        subscriberslist = []
#        errorcandidates = []
#        for index, parsedline in enumerate(reader):
#            if index == 0:
#                if header_row_present:
#                    fields = parsedline
#                    continue
#                else:
#                    fields = field.Fields(composer.schema).keys()
#            if len(parsedline)<len(fields):
#                pass
#            else:
#                try:
#                    subscriber = dict(zip(fields,\
#                       map(lambda x:x.decode(charset), parsedline)))
#                    check_email(subscriber['email'])
#                except:
#                    errorcandidates.append(subscriber['email'])
#                else:
#                    subscriberslist.append(subscriber)
#        return subscriberslist, errorcandidates
#    except Exception, e:
#        return _(u"Error importing subscriber file. %s" % e), []
#
#
#class UploadForm(crud.AddForm):
#    label = _(u"Upload")
#
#    @property
#    def fields(self):
#        subscriberdata = schema.Bytes(
#            __name__ = 'subscriberdata',
#            title=_(u"Subscribers"),
#            description=_(u"Upload a CSV file with a list of subscribers here. "
#                          u"Subscribers already present in the database will "
#                          u"be overwritten. Each line should contain: "
#                          u"${columns}.",
#                          mapping=dict(columns=';'.join(field.Fields(
#                                         self.context.composer.schema).keys())))
#        )
#        remove = schema.Bool(__name__ = 'removenonexisting',
#            title=_(u"Remove non-existing"),
#            description=_(u"If selected and a subscriber exists in the "
#                          u"database, but is not part of the uploaded file, "
#                          u"the subscriber will be removed from the list."),
#            default = False
#        )
#        header_row_present = schema.Bool(__name__ = 'header_row_present',
#            title=_(u"CSV contains a header row"),
#            description=_(u"Select this if you want to use the csv "
#                          u"header row to designate document variables."
#                          u"The header row must contain one 'email' field."),
#            default = False
#        )
#        csv_delimiter = schema.TextLine(__name__ = 'csv_delimiter',
#            title=_(u"CSV delimiter"),
#            description=_(u"The delimiter in your CSV file. "
#                          u"(Usually ',' or ';', but no quotes are necessary.)"),
#            default = u','
#        )
#
#        return field.Fields(subscriberdata, remove,
#                            header_row_present, csv_delimiter)
#
#    @property
#    def mychannel(self):
#        return self.context.context
#
#    def _removeSubscription(self, secret):
#        """Removes subscription based on secret.
#        """
#        current = self.mychannel.subscriptions
#        old_subscription = current.query(format=self.context.format,
#                                        secret=secret)
#        if not len(old_subscription):
#            return None
#        old_subscription = tuple(old_subscription)
#        old_collector_data = old_subscription[0].collector_data
#        for sub in old_subscription:
#            current.remove_subscription(sub)
#        return old_subscription
#
#    def _addItem(self, data):
#        """imports csv and returns message
#
#        @param data: the form data
#        @return status as i18n aware unicode
#
#        if a subscription with same email is found, we delete this first
#        but keep selection of options.
#
#        if remove-non-existing in the form was found, all existing subscriptions
#        not found in the CSV file are removed.
#        """
#
#        metadata = dict(format=self.context.format,
#                        date=datetime.datetime.now())
#
#        subscriberdata = data.get('subscriberdata', None)
#        remove = data.get('removenonexisting', False)
#        header_row_present = data.get('header_row_present', False)
#        delimiter = data.get('csv_delimiter', csv_delimiter)
#        if subscriberdata is None:
#            return _(u"File was not given.")
#        subscribers, errorcandidates = parseSubscriberCSVFile(subscriberdata,
#                                self.context.composer,
#                                header_row_present=header_row_present,
#                                delimiter=delimiter)
#        if not type(subscribers)==type([]):
#            return _(u"File has incorrect format.")
#        added = 0
#        new_and_updated = []
#        notadded = len(errorcandidates)
#        current = self.mychannel.subscriptions
#        if remove:
#            old = sets.Set([sub.composer_data['email'] \
#                            for sub in current.values()])
#        for subscriber_data in subscribers:
#            secret = collective.singing.subscribe.secret(self.mychannel,
#                                                         self.context.composer,
#                                                         subscriber_data,
#                                                         self.context.request)
#            try:
#                old_subscription = self._removeSubscription(secret)
#                item = current.add_subscription(self.mychannel, secret,
#                                                subscriber_data, [], metadata)
#                new_and_updated.append(subscriber_data['email'])
#                # restore section selection
#                if old_subscription is not None:
#                    old_collector_data = old_subscription[0].collector_data
#                    if 'selected_collectors' in old_collector_data \
#                       and old_collector_data['selected_collectors']:
#                        item.collector_data = old_collector_data
#                added += 1
#            except Exception, e: # XXX refine which exceptions we want to catch
#                # TODO; put some information about error e into the message
#                errorcandidates.append(subscriber_data.get('email',
#                                                           _(u'Unknown')))
#                notadded += 1
#        removed = 0
#        if remove:
#            for email in old.difference(sets.Set(new_and_updated)):
#                for key in current.keys():
#                    if key.startswith(email):
#                        current.remove_subscription(current[key])
#                        removed += 1
#                        break
#        if notadded:
#            msg = _(u"${numberadded} subscriptions updated successfully. "
#                    u"${numberremoved} removed. "
#                    u"${numbernotadded} could not be added. "
#                    u"(${errorcandidates})",
#                    mapping=dict(numbernotadded=str(notadded),
#                                 numberremoved=str(removed),
#                                 errorcandidates=', '.join(errorcandidates),
#                                 numberadded=str(added))
#                    )
#        elif removed > 0:
#            msg = _(u"${numberadded} subscriptions updated successfully, "
#                    u"${numberremoved} removed!",
#                    mapping=dict(numberadded=str(added),
#                                 numberremoved=str(removed))
#                    )
#        else:
#            msg = _(u"${numberadded} subscriptions updated successfully!",
#                    mapping=dict(numberadded=str(added),))
#        return msg
#
#    @z3c.form.button.buttonAndHandler(_('Upload'), name='upload')
#    def handle_add(self, action):
#        data, errors = self.extractData()
#        if errors:
#            self.status = form.EditForm.formErrorsMessage
#            return
#        try:
#            self.status = self._addItem(data)
#        except Exception, e:
#            if DevelopmentMode:
#                raise
#            self.status = e
#
#    @z3c.form.button.buttonAndHandler(_('Download'), name='download')
#    def handle_download(self, action):
#        self.status = _(u"Subscribers exported.")
#        return self.request.response.redirect(self.mychannel.absolute_url() + \
#                                              '/export')
#
#class ManageUploadForm(crud.CrudForm):
#    description = _(u"Upload list of subscribers.")
#
#    format = None
#    composer = None
#
#    editform_factory = crud.NullForm
#    addform_factory = UploadForm
#
#    @property
#    def prefix(self):
#        return self.format