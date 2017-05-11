# -*- coding: utf-8 -*-
from email.Header import Header
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import formatdate
from Products.CMFCore.utils import getToolByName
from Products.EasyNewsletter.config import IS_PLONE_5
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface
import email
import formatter
import htmllib
import StringIO
import traceback
import zope.sendmail.interfaces

if not IS_PLONE_5:  # BBB
    from zope.site.hooks import getSite
    from Products.MailHost.interfaces import IMailHost
else:
    from plone.registry.interfaces import IRegistry
    from Products.CMFPlone.interfaces.controlpanel import IMailSchema


class IPortalMailSettings(Interface):
    """ PortalMailSettings proxy interface
    """


class PortalMailSettings(object):
    """ PortalMailSettings proxy
    """

    def __init__(self):
        self.settings = {}

    def __getattr__(self, key):
        if not IS_PLONE_5:  # BBB
            portal = getSite()
            mail_host = getUtility(IMailHost)
            key_map = {
                'smtp_host': 'smtp_host',
                'smtp_port': 'smtp_port',
                'smtp_userid': 'smtp_uid',
                'smtp_pass': 'smtp_pwd',
            }
            if key in key_map:
                return getattr(mail_host, key, '')
            elif key == 'email_from_address':
                return portal.getProperty(key)
            elif key == 'email_from_name':
                return portal.getProperty(key)
            elif key == 'email_charset':
                return portal.getProperty(key)
        else:
            self.registry = getUtility(IRegistry)
            reg_mail = self.registry.forInterface(
                IMailSchema, prefix='plone')
            self.settings['smtp_host'] = reg_mail.smtp_host
            self.settings['smtp_port'] = reg_mail.smtp_port
            self.settings['smtp_userid'] = reg_mail.smtp_userid
            self.settings['smtp_pass'] = reg_mail.smtp_pass
            self.settings['email_from_address'] = reg_mail.email_from_address
            self.settings['email_from_name'] = reg_mail.email_from_name
            self.settings['email_charset'] = reg_mail.email_charset
        return self.settings.get(key)


def get_portal_mail_settings():
    return PortalMailSettings()


def get_email_charset():
    if not IS_PLONE_5:  # BBB
        portal = getSite()
        props = getToolByName(portal, 'portal_properties').site_properties
        return props.getProperty('default_charset')
    else:
        registry = getUtility(IRegistry)
        return registry.get('plone.email_charset', 'utf-8')


class IDispatch(Interface):
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
        formtext = formatter.AbstractFormatter(
            formatter.DumbWriter(textout, plain_text_maxcols))
        parser = htmllib.HTMLParser(formtext)
        parser.feed(html)
        parser.close()

        # append the anchorlist at the bottom of a message
        # to keep the message readable.
        counter = 0
        anchorlist = "\n\n" + ("-" * plain_text_maxcols) + "\n\n"
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
    # maybe later :)  msg['From'] = Header("%s <%s>" %
    #   (send_from_name, send_from), encoding)
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
    alternatives.attach(MIMEText(text, 'plain', _charset=encoding))
    alternatives.attach(MIMEText(html, 'html', _charset=encoding))

    return msg


# XXX verify if this is in use, seems not the case
@implementer(IDispatch)
@adapter(email.Message.Message)
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
      ComponentLookupError: (<InterfaceClass \
              zope.sendmail.interfaces.IMailDelivery>, '')

    Let's provide our own ``IMailDelivery`` and see what happens:

      >>> class MyMailDelivery(object):
      ...     interface.implements(zope.sendmail.interfaces.IMailDelivery)
      ...
      ...     def send(self, from_, to, message):
      ...         print 'From: ', from_  # noqa
      ...         print 'To: ', ', '.join(to)  # noqa
      ...         print 'Message follows:'  # noqa
      ...         print message  # noqa

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
      >>> print message # doctest: +NORMALIZE_WHITESPACE # noqa
      Traceback (most recent call last):
      MyException: This is a test
    """

    def __init__(self, message):
        self.message = message

    def __call__(self):
        msg = self.message
        delivery = getUtility(zope.sendmail.interfaces.IMailDelivery)
        try:
            delivery.send(msg['From'], self._split(msg['To']), msg.as_string())
        except Exception, e:  # noqa
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
          ['Daniel Nouri <daniel.nouri@gmail.com>',
                  'Daniel Widerin <daniel.widerin@kombinat.at>']
          >>> split('"Daniel flash, dance Nouri" <daniel.nouri@gmail.com>,'
          ...       '"Daniel Saily Widerin" <daniel.widerin@kombinat.at>')
          ['"Daniel flash, dance Nouri" <daniel.nouri@gmail.com>',
                  '"Daniel Saily Widerin" <daniel.widerin@kombinat.at>']
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
