# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from plone import api
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.EasyNewsletter import _
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getUtility

import csv
import logging
import six


if six.PY2:
    import codecs
else:
    from io import TextIOWrapper

log = logging.getLogger('Products.EasyNewsletter')


def normalize_id(astring):
    return getUtility(IIDNormalizer).normalize(astring)


CSV_HEADER = [
    u'salutation',
    u'name_prefix',
    u'firstname',
    u'lastname',
    # u'nl_language',
    u'email',
    u'organization'
]


class NewsletterSubscribersUpload(BrowserView):

    def __call__(self):
        return self.index()

    def create_subscribers(self):
        """Create newsletter subscribers from uploaded CSV file.
        """
        # Do nothing if no submit button was hit
        if 'form.button.Import' not in self.request.form:
            return

        context = aq_inner(self.context)
        lang = context.Language()
        # plone_utils = getToolByName(self.context, 'plone_utils')
        # encoding = plone_utils.getSiteEncoding()
        existing = []
        subscribers = api.content.find(context=self.context,
                                       portal_type='Newsletter Subscriber')
        for subscriber in subscribers:
            existing.append(subscriber.email.lower())

        # messages = IStatusMessage(self.request)
        success = []
        fail = []

        # Show error if no file was specified
        filename = self.request.form.get('csv_upload', None)
        if not filename:
            msg = _('No file specified.')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return self.request.response.redirect(
                context.absolute_url() + '/subscribers-upload')

        reader = UnicodeReader(filename)
        header = next(reader)
        if header != [x for x in CSV_HEADER]:
            log.info("Got header %s\n Expected:%s" % (
                header, CSV_HEADER))
            msg = _(
                'Wrong specification of the CSV file. '
                + 'Please correct it and retry.')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return self.request.response.redirect(
                context.absolute_url() + '/subscribers-upload')

        for subscriber in reader:
            # Check the length of the line
            if len(subscriber) != 6:
                msg = _(
                    u'enl_subscriber_upload_wrong_number_of_columns',
                    default=u'The number of columns in the row is not correct. \
                        It should be 6. Check your CSV file.')
                fail.append(
                    {'failure': msg})
            else:
                salutation = subscriber[0]
                name_prefix = subscriber[1]
                firstname = subscriber[2]
                lastname = subscriber[3]
                # nl_language = subscriber[4]
                email = subscriber[4].lower()
                organization = subscriber[5]
                id = normalize_id(email)
                if email in existing:
                    # If subscriber with email exists, update user info
                    sub = api.content.find(context=self.context,
                                           email=email)
                    if len(sub) > 1:
                        msg = _('More than one subscriber with this email '
                                'address existed, subscriber info was NOT '
                                'updated. Check manually!')
                        fail.append(
                            {'salutation': salutation,
                             'name_prefix': name_prefix,
                             'firstname': firstname,
                             'lastname': lastname,
                             # 'nl_language': nl_language,
                             'email': email,
                             'organization': organization,
                             'failure': msg})
                    else:
                        sub = sub[0].getObject()
                        sub.email = email
                        sub.name_prefix = name_prefix
                        sub.firstname = firstname
                        sub.lastname = lastname
                        # sub.nl_language = nl_language
                        sub.organization = organization
                        sub.salutation = salutation
                        sub.title = email + " - " + ' '.join([lastname,
                                                             firstname])
                        sub.reindexObject()
                        msg = _('Email existed, updated subscriber.')
                        success.append(
                            {'salutation': salutation,
                             'name_prefix': name_prefix,
                             'firstname': firstname,
                             'lastname': lastname,
                             # 'nl_language': nl_language,
                             'email': email,
                             'organization': organization,
                             'success': msg,
                             }
                        )
                else:
                    # If it doesn't exist, create subscriber
                    title = email + " - " + ' '.join([lastname,
                                                      firstname])
                    try:
                        api.content.create(
                            type='Newsletter Subscriber',
                            container=self.context,
                            id=id,
                            title=title,
                            description="",
                            language=lang,
                            name_prefix=name_prefix,
                            email=email,
                            firstname=firstname,
                            lastname=lastname,
                            organization=organization,
                            # nl_language=nl_language,
                            salutation=salutation,
                        )
                        # update existing
                        existing.append(email)
                        msg = _('Subscriber created.')
                        success.append({
                            'salutation': salutation,
                            'name_prefix': name_prefix,
                            'firstname': firstname,
                            'lastname': lastname,
                            # 'nl_language': nl_language,
                            'email': email,
                            'organization': organization,
                            'success': msg})

                    except Exception as e:
                        fail.append({
                            'salutation': salutation,
                            'name_prefix': name_prefix,
                            'firstname': firstname,
                            'lastname': lastname,
                            # 'nl_language': nl_language,
                            'email': email,
                            'organization': organization,
                            'failure':
                                'An error occured while creating this subscriber: %s' % str(e)
                        })

        return {'success': success, 'fail': fail}


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        if six.PY2:
            self.reader = codecs.getreader(encoding)(f)
        else:
            self.reader = TextIOWrapper(f, encoding=encoding)

    def __iter__(self):
        return self

    def __next__(self):
        data = next(self.reader)
        if six.PY2:
            data = data.encode("utf-8")
        return data
    next = __next__  # BBB for Python2


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def __next__(self):
        row = next(self.reader)
        return row

    next = __next__  # BBB for Python2

    def __iter__(self):
        return self
