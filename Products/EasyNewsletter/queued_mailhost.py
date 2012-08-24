import logging
import socket
from threading import Lock
from os.path import realpath

from AccessControl.SecurityInfo import ClassSecurityInfo
from AccessControl.Permissions import change_configuration, view

from zope.app.component.hooks import getSite

from zope.interface import implements

from zope.sendmail.mailer import SMTPMailer as BaseSMTPMailer
from zope.sendmail.maildir import Maildir
from zope.sendmail.delivery import DirectMailDelivery
from zope.sendmail.delivery import QueuedMailDelivery
from zope.sendmail.delivery import QueueProcessorThread

from Products.CMFCore.utils import getToolByName
from Products.MailHost.interfaces import IMailHost


ssl_support = False
if hasattr(socket, 'ssl'):
    ssl_support = True

LOG = logging.getLogger('QueuedMailHost')

queue_threads = {}  # maps MailHost path -> queue processor threada


class SMTPMailer(BaseSMTPMailer):

    def __init__(self, hostname='localhost', port=25,
                 username=None, password=None, **kw):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.forceTLS = kw.get('forceTLS', False)
        self.noTLS =  kw.get('noTLS', False)

    def send(self, fromaddr, toaddrs, message):
        connection = self.smtp(self.hostname, str(self.port))

        # avoid "SMTPException: SMTP AUTH extension not supported by server."
        # probably this stuff should go into zope.sendmail itself
        if not (200 <= connection.ehlo()[0] <= 299):
            (code, resp) = connection.helo()
            if not (200 <= code <= 299):
                raise MailHostError('Host refused to talk to us: %s' % resp)

        if connection.has_extn('starttls') and ssl_support and not self.noTLS:
            connection.starttls()
            connection.ehlo()
        elif self.forceTLS:
            if self.noTLS:
                raise MailHostError('Configured not to try TLS '
                    'but it is required')
            else:
                raise MailHostError('Host does NOT support StartTLS '
                    'but it is required')
        if connection.does_esmtp and self.username:
            connection.login(self.username, self.password)
        connection.sendmail(fromaddr, toaddrs, message)
        connection.quit()


def synchronized(lock):
    """ Decorator for method synchronization. """

    def wrapper(f):
        def method(*args, **kw):
            lock.acquire()
            try:
                return f(*args, **kw)
            finally:
                lock.release()
        return method
    return wrapper


class QueuedMailHost(object):
    """ almost bare c/p of Products.MailHost.MailHost.MailBase
    which is only available on plone 4
    """

    implements(IMailHost)

    security = ClassSecurityInfo()
    smtp_uid = '' # Class attributes for smooth upgrades
    smtp_pwd = ''
    smtp_queue = True
    smtp_queue_directory = '/tmp'
    forceTLS = False
    noTLS = False
    lock = Lock()

    def _makeMailer(self, context=None):
        """ Create a SMTPMailer """
        if context is None:
            context = getSite()
        mailhost = getToolByName(context,'MailHost')
        if mailhost:
            self.smtp_host = mailhost.smtp_host
            self.smtp_port = mailhost.smtp_port
            self.smtp_uid = mailhost._smtp_userid
            self.smtp_pwd = mailhost._smtp_pass
            self.noTLS = mailhost.smtp_notls
        mailer = SMTPMailer(hostname=self.smtp_host,
                          port=int(self.smtp_port),
                          username=self.smtp_uid or None,
                          password=self.smtp_pwd or None,
                          noTLS = self.noTLS,
                          )
        return mailer

    security.declarePrivate('_getThreadKey')
    def _getThreadKey(self):
        """ Return the key used to find our processor thread.
        """
        return realpath(self.smtp_queue_directory)

    @synchronized(lock)
    def _stopQueueProcessorThread(self):
        """ Stop thread for processing the mail queue.
        """
        key = self._getThreadKey()
        if key in queue_threads:
            thread = queue_threads[key]
            thread.stop()
            while thread.isAlive():
                # wait until thread is really dead
                time.sleep(0.3)
            del queue_threads[key]
            LOG.info('Thread for %s stopped' % key)

    @synchronized(lock)
    def _startQueueProcessorThread(self):
        """ Start thread for processing the mail queue.
        """
        key = self._getThreadKey()
        if key not in queue_threads:
            thread = QueueProcessorThread()
            thread.setMailer(self._makeMailer())
            thread.setQueuePath(self.smtp_queue_directory)
            thread.start()
            queue_threads[key] = thread
        LOG.info('Thread for %s started' % key)

    security.declareProtected(view, 'queueLength')
    def queueLength(self):
        """ return length of mail queue """
        try:
            maildir = Maildir(self.smtp_queue_directory)
            return len([item for item in maildir])
        except ValueError:
            return 'n/a - %s is not a maildir - please verify your ' \
                   'configuration' % self.smtp_queue_directory

    security.declareProtected(view, 'queueThreadAlive')
    def queueThreadAlive(self):
        """ return True/False is queue thread is working
        """
        th = queue_threads.get(self._getThreadKey())
        if th:
            return th.isAlive()
        return False

    security.declarePrivate('_send')
    def _send(self, mfrom, mto, msg, immediate=False):
        """ Send the message """

        if self.smtp_queue:
            # Start queue processor thread, if necessary
            self._startQueueProcessorThread()
            delivery = QueuedMailDelivery(self.smtp_queue_directory)
        else:
            delivery = DirectMailDelivery(self._makeMailer())
        delivery.send(mfrom, mto, msg)

    def send(self, msg, mto=[], mfrom="", subject="", encode=None):
        """Send email
        """
        if not isinstance(mto,list):
            mto = [mto]
        return self._send(mfrom, mto, msg)
