import OFS
import re

from Acquisition import aq_inner
from email.MIMEText import MIMEText
from email.Header import Header
from zope.component import queryUtility
from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from Products.EasyNewsletter.interfaces import IENLRegistrationTool
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _

import logging
logger = logging.getLogger("Products.EasyNewsletter.registration")


class SubscriberView(BrowserView):
    """
    """

    def portal_state(self):
        context = aq_inner(self.context)
        return getMultiAdapter((context, self.request), name=u'plone_portal_state')

    @property
    def portal(self):
        pstate = self.portal_state()
        return pstate.portal()

    @property
    def portal_url(self):
        pstate = self.portal_state()
        return pstate.portal_url()

    def register_subscriber(self):
        """
        """
        subscriber = self.request.get("subscriber")
        fullname = self.request.get("fullname", "")
        salutation = self.request.get("salutation", "")
        organization = self.request.get("organization", "")
        subscription = self.request.get("subscription", "")
        path_to_easynewsletter = self.request.get("newsletter")
        # remove leading slash from paths like: /mynewsletter
        path_to_easynewsletter = path_to_easynewsletter.strip('/')
        newsletter_container = self.portal.restrictedTraverse(path_to_easynewsletter)
        messages = IStatusMessage(self.request)
        if not subscriber:
            messages.addStatusMessage(_("Please enter a valid email address."), "error")
            return self.request.response.redirect(newsletter_container.absolute_url())
        from Products.validation.validators.BaseValidators import EMAIL_RE
        EMAIL_RE = "^" + EMAIL_RE
        mo = re.search(EMAIL_RE, subscriber)
        if not mo:
            messages.addStatusMessage(_("Please enter a valid email address."), "error")
            return self.request.response.redirect(newsletter_container.absolute_url())

        subscriber_info = newsletter_container.getSubscriberInfo(subscriber)
        subscribed = subscriber_info is not None
        if subscription == "unsubscription" and subscribed:
            msg_subject = newsletter_container.unsubscriber_confirmation_mail_subject
            msg_text = newsletter_container.getRawUnsubscriber_confirmation_mail_text()
            confirmation_url = newsletter_container.absolute_url() + "/unsubscribe?subscriber=" + subscriber_info['UID']
            msg_text = msg_text.replace("${confirmation_url}", confirmation_url)
        elif subscription == "unsubscription":
            msg_subject = newsletter_container.unsubscriber_not_mail_subject
            msg_text = newsletter_container.getRawUnsubscriber_not_mail_text()
        elif subscribed:
            msg_subject = newsletter_container.subscriber_already_mail_subject
            msg_text = newsletter_container.getRawSubscriber_already_mail_text()
        else:
            msg_subject = newsletter_container.subscriber_confirmation_mail_subject
            msg_text = newsletter_container.getRawSubscriber_confirmation_mail_text()
            subscriber_data = {}
            subscriber_data["subscriber"] = subscriber
            subscriber_data["fullname"] = fullname
            subscriber_data["salutation"] = salutation
            subscriber_data["organization"] = organization
            subscriber_data["path_to_easynewsletter"] = path_to_easynewsletter
            # use password reset tool to create a hash
            pwr_data = self._requestReset(subscriber)
            hashkey = pwr_data['randomstring']
            enl_registration_tool = queryUtility(IENLRegistrationTool, 'enl_registration_tool')
            if hashkey in enl_registration_tool.objectIds():
                logger.warning(u"hashkey [%s] in ids", hashkey)
                messages.addStatusMessage(_("Sorry... An error has happend during operation."), "error")
                return self.request.response.redirect(newsletter_container.absolute_url())
            enl_registration_tool[hashkey] = RegistrationData(hashkey, **subscriber_data)
            confirmation_url = self.portal_url + '/confirm-subscriber?hkey=' + str(hashkey)
            msg_text = msg_text.replace("${confirmation_url}", confirmation_url)

        msg_subject = msg_subject.replace("${portal_url}", self.portal_url.strip('http://'))
        msg_text = msg_text.replace("${newsletter_title}", newsletter_container.Title())
        msg_text = msg_text.replace("${subscriber_email}", subscriber)

        props = getToolByName(self, "portal_properties").site_properties
        charset = props.getProperty("default_charset")
        msg = MIMEText(msg_text, "plain", charset)
        msg['To']= Header(subscriber)
        msg['From'] = newsletter_container.getRegistrationSender()
        msg['Subject'] = Header(msg_subject)
        try:
            MailHost = newsletter_container.getMailHost(mode = 'subscription')
        except Exception, e:
            messages.addStatusMessage(_("Sorry... An error has happend during operation."), "error")
            return self.request.response.redirect(newsletter_container.absolute_url())
        MailHost.send(msg.as_string())
        messages.addStatusMessage(_("Your request has been registered. An email was sent to you. It contains a link to confirm your request."), "info")
        self.request.response.redirect(newsletter_container.absolute_url())

    def confirm_subscriber(self):
        hashkey = self.request.get('hkey')
        enl_registration_tool = queryUtility(IENLRegistrationTool, 'enl_registration_tool')
        regdataobj = enl_registration_tool.get(hashkey)
        messages = IStatusMessage(self.request)
        if regdataobj:
            easynewsletter = self.portal.restrictedTraverse(regdataobj.path_to_easynewsletter)
            if easynewsletter.getSubscriberInfo(regdataobj.subscriber) is not None:
                del enl_registration_tool[hashkey]
                messages.addStatusMessage(_('This email address is already registered.'))
            else:
                result_add = easynewsletter.addSubscriber(regdataobj.subscriber, regdataobj.fullname, regdataobj.organization, regdataobj.salutation)
                if result_add:
                    del enl_registration_tool[hashkey]
                    messages.addStatusMessage(_("Your subscription was successfully confirmed."))
                else:
                    messages.addStatusMessage(_("Sorry... An error has happend during operation."), "error")
            return self.request.response.redirect(easynewsletter.absolute_url())
        else:
            messages.addStatusMessage(_("No registration found. The link you used may be too old."), "error")
        return self.request.response.redirect(self.portal.absolute_url())

    def _requestReset(self, userid):
        """Ask the system to start the password reset procedure for
        user 'userid'.

        Returns a dictionary with the random string that must be
        used to reset the password in 'randomstring', the expiration date
        as a DateTime in 'expires', and the userid (for convenience) in
        'userid'.
        ### taken from Products.PasswordResetTool and but without getValidUser check!
        """
        pwrtool = getToolByName(self.context, 'portal_password_reset')
        randomstring = pwrtool.uniqueString(userid)
        expiry = pwrtool.expirationDate()
        pwrtool._requests[randomstring] = (userid, expiry)
        pwrtool.clearExpired(10)   # clear out untouched records more than 10 days old
                                # this is a cheap sort of "automatic" clearing
        pwrtool._p_changed = 1
        retval = {}
        retval['randomstring'] = randomstring
        retval['expires'] = expiry
        retval['userid'] = userid
        return retval


class RegistrationData(OFS.SimpleItem.SimpleItem):
    """ holds data from OnlineMemberSignupForm
    """

    def __init__(self, id, **kw):
        self.id = id
        for key, value in kw.items():
            setattr(self, key, value)
        super(RegistrationData, self).__init__(id)

    @property
    def title(self):
        return "%s - %s" % (self.fullname, self.subscriber)
