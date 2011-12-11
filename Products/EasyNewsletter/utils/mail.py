# This code has been shamelessly stolen from collective.singing.
import formatter
import htmllib
import quopri
import StringIO
import traceback
import email

from email.Header import Header
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import formatdate

from zope import interface
from zope import component
import zope.sendmail.interfaces


class IDispatch(interface.Interface):
    """Dispatchers adapt message *payloads* and send them."""

    def __call__():
        """Attempt to send message.

        Must return a tuple ``(status, status_message)``.  See
        ``MESSAGE_STATES`` for possible choices for the status.  The
        status message may be None or a text containing details about
        the status, e.g. why it failed.

        If this method raises an exception, an 'error' is assumed.
        """
        

def create_html_mail(subject, html, text=None, from_addr=None, to_addr=None,
                     headers=None, encoding='UTF-8'):
    """Create a mime-message that will render HTML in popular
    MUAs, text in better ones.
    """
    # Use DumbWriters word wrapping to ensure that no text line
    # is longer than plain_text_maxcols characters.
    plain_text_maxcols = 72

    html = html.encode(encoding)
    if text is None:
        # Produce an approximate textual rendering of the HTML string,
        # unless you have been given a better version as an argument
        textout = StringIO.StringIO()
        formtext = formatter.AbstractFormatter(formatter.DumbWriter(
                        textout, plain_text_maxcols))
        parser = htmllib.HTMLParser(formtext)
        parser.feed(html)
        parser.close()

        # append the anchorlist at the bottom of a message
        # to keep the message readable.
        counter = 0
        anchorlist  = "\n\n" + ("-" * plain_text_maxcols) + "\n\n"
        for item in parser.anchorlist:
            counter += 1
            anchorlist += "[%d] %s\n" % (counter, item)

        text = textout.getvalue() + anchorlist
        del textout, formtext, parser, anchorlist
    else:
        text = text.encode(encoding)

    # if we would like to include images in future, there should
    # probably be 'related' instead of 'mixed'
    msg = MIMEMultipart('mixed')
    # maybe later :)  msg['From'] = Header("%s <%s>" % (send_from_name, send_from), encoding)
    msg['Subject'] = Header(subject, encoding)
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Date'] = formatdate(localtime=True)
    msg["Message-ID"] = email.Utils.make_msgid()
    if headers:
        for key, value in headers.items():
            msg[key] = value
    msg.preamble = 'This is a multi-part message in MIME format.'

    alternatives = MIMEMultipart('alternative')
    msg.attach(alternatives)
    alternatives.attach( MIMEText(text, 'plain', _charset=encoding) )
    alternatives.attach( MIMEText(html, 'html',  _charset=encoding) )

    return msg

class Dispatch(object):
    """An IDispatcher registered for ``email.message.Message`` that'll
    send e-mails using ``zope.sendmail``.

    To send a test e-mail, we'll first create an e-mail object:

      >>> message = email.Message.Message()
      >>> message['From'] = 'daniel@testingunderground.com'
      >>> message['To'] = 'plone-users@lists.sourceforge.net'
      >>> message.set_payload('Hello, Plone users!')

    ``Dispatch`` adapts ``email.Message.Message``:

      >>> dispatcher = Dispatch(message)

    Sending a message without a configured ``IMailDelivery`` will fail:

      >>> dispatcher() # doctest: +ELLIPSIS
      Traceback (most recent call last):
      ...
      ComponentLookupError: (<InterfaceClass zope.sendmail.interfaces.IMailDelivery>, '')

    Let's provide our own ``IMailDelivery`` and see what happens:

      >>> class MyMailDelivery(object):
      ...     interface.implements(zope.sendmail.interfaces.IMailDelivery)
      ...
      ...     def send(self, from_, to, message):
      ...         print 'From: ', from_
      ...         print 'To: ', ', '.join(to)
      ...         print 'Message follows:'
      ...         print message

      >>> component.provideUtility(MyMailDelivery())
      >>> dispatcher()
      From:  daniel@testingunderground.com
      To:  plone-users@lists.sourceforge.net
      Message follows:
      From: daniel@testingunderground.com
      To: plone-users@lists.sourceforge.net
      <BLANKLINE>
      Hello, Plone users!
      (u'sent', None)

    Note that the last line is the return value.

    If the delivery fails, we'll get a return value with u'error' as
    the first element.

      >>> class MyException(Exception):
      ...     pass
      >>> class MyFailingMailDelivery(object):
      ...     interface.implements(zope.sendmail.interfaces.IMailDelivery)
      ...
      ...     def send(self, from_, to, message):
      ...         raise MyException('This is a test')
      >>> component.provideUtility(MyFailingMailDelivery())
      >>> status, message = dispatcher()
      >>> status
      u'error'
      >>> print message # doctest: +NORMALIZE_WHITESPACE
      Traceback (most recent call last):
      MyException: This is a test
    """

    interface.implements(IDispatch)
    component.adapts(email.Message.Message)

    def __init__(self, message):
        self.message = message

    def __call__(self):
        msg = self.message
        delivery = component.getUtility(zope.sendmail.interfaces.IMailDelivery)
        try:
            delivery.send(msg['From'], self._split(msg['To']), msg.as_string())
        except Exception, e:
            # TODO: log
            return u'error', traceback.format_exc(e)
        else:
            return u'sent', None

    @staticmethod
    def _split(value):
        """
          >>> split = Dispatch._split
          >>> split('"Daniel flash, Nouri" <daniel.nouri@gmail.com>')
          ['"Daniel flash, Nouri" <daniel.nouri@gmail.com>']
          >>> split('Daniel Nouri <daniel.nouri@gmail.com>, '
          ...       'Daniel Widerin <daniel.widerin@kombinat.at>')
          ['Daniel Nouri <daniel.nouri@gmail.com>', 'Daniel Widerin <daniel.widerin@kombinat.at>']
          >>> split('"Daniel flash, dance Nouri" <daniel.nouri@gmail.com>,'
          ...       '"Daniel Saily Widerin" <daniel.widerin@kombinat.at>')
          ['"Daniel flash, dance Nouri" <daniel.nouri@gmail.com>', '"Daniel Saily Widerin" <daniel.widerin@kombinat.at>']
        """
        items = []
        last_index = 0
        for i, c in enumerate(value):
            if c == ',':
                if value[:i].count('"') % 2 == 0:
                    items.append(value[last_index:i].strip())
                    last_index = i + 1
        last_item = value[last_index:]
        if last_item.strip():
            items.append(last_item.strip())
        return items
