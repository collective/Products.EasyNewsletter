# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from plone import api
from Products.Five.browser import BrowserView

import codecs
import csv
import six
import tempfile


CSV_HEADER = [
    u"salutation",
    u"name_prefix",
    u"firstname",
    u"lastname",
    # u"nl_language",
    u"email",
    u"organization",
]


class NewsletterSubscribersDownload(BrowserView):
    def __call__(self):
        context = aq_inner(self.context)
        # Create CSV file
        filename = tempfile.mktemp()
        file = open(filename, "wb")
        csvWriter = UnicodeWriter(
            file, {"delimiter": ",", "quotechar": '"', "quoting": csv.QUOTE_MINIMAL}
        )
        csvWriter.writerow([x for x in CSV_HEADER])
        for subscriber in api.content.find(
            portal_type="Newsletter Subscriber", context=self.context, sort_on="email"
        ):
            obj = subscriber.getObject()
            csvWriter.writerow(
                [
                    obj.salutation,
                    obj.name_prefix,
                    obj.firstname,
                    obj.lastname,
                    # obj.nl_language,
                    obj.email,
                    obj.organization,
                ]
            )
        file.close()
        data = open(filename, "r").read()

        # Create response
        response = context.REQUEST.response
        response.addHeader(
            "Content-Disposition", "attachment; filename=easynewsletter-subscribers.csv"
        )
        response.addHeader("Content-Type", "text/csv")
        response.addHeader("Content-Length", "%d" % len(data))
        response.addHeader("Pragma", "no-cache")
        response.addHeader(
            "Cache-Control", "must-revalidate, post-check=0, pre-check=0, public"
        )
        response.addHeader("Expires", "0")

        # Return CSV data
        return data


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = six.cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        row = [s or u'' for s in row]
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
