# -*- coding: utf-8 -*-
from AccessControl.SecurityManagement import newSecurityManager
from Acquisition import aq_inner
from email.MIMEText import MIMEText
from plone import api
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.protect.interfaces import IDisableCSRFProtection
from Products.CMFCore.utils import getToolByName
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _
from Products.EasyNewsletter.config import MESSAGE_CODE
from Products.EasyNewsletter.interfaces import IENLRegistrationTool
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from Products.validation.validators.BaseValidators import EMAIL_RE
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.interface import alsoProvides
import OFS
import re

EMAIL_RE = "^" + EMAIL_RE


class SubscriberView(BrowserView):
    """
    """

    def portal_state(self):
        context = aq_inner(self.context)
        return getMultiAdapter(
            (context, self.request), name=u'plone_portal_state')

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
        path_to_easynewsletter = self.request.get("newsletter")
        # remove leading slash from paths like: /mynewsletter
        path_to_easynewsletter = path_to_easynewsletter.strip('/')
        newsletter_container = self.portal.restrictedTraverse(
            path_to_easynewsletter)
        messages = IStatusMessage(self.request)
        if not subscriber:
            messages.addStatusMessage(
                _("Please enter a valid email address."), "error")
            return self.request.response.redirect(
                newsletter_container.absolute_url())
        from Products.validation.validators.BaseValidators import EMAIL_RE
        EMAIL_RE = "^" + EMAIL_RE
        mo = re.search(EMAIL_RE, subscriber)
        if not mo:
            messages.addStatusMessage(
                _("Please enter a valid email address."), "error")
            return self.request.response.redirect(
                newsletter_container.absolute_url())
        norm = queryUtility(IIDNormalizer)
        normalized_subscriber = norm.normalize(subscriber)
        if normalized_subscriber in newsletter_container.objectIds():
            messages.addStatusMessage(
                _("Your email address is already registered."), "error")
            return self.request.response.redirect(
                newsletter_container.absolute_url())
        subscriber_data = {}
        subscriber_data["subscriber"] = subscriber
        subscriber_data["fullname"] = fullname
        subscriber_data["salutation"] = salutation
        subscriber_data["organization"] = organization
        subscriber_data["path_to_easynewsletter"] = path_to_easynewsletter

        # use password reset tool to create a hash
        pwr_data = self._requestReset(subscriber)
        hashkey = pwr_data['randomstring']
        enl_registration_tool = queryUtility(
            IENLRegistrationTool, 'enl_registration_tool')
        if hashkey not in enl_registration_tool.objectIds():
            enl_registration_tool[hashkey] = RegistrationData(
                hashkey, **subscriber_data)
            msg_subject = newsletter_container\
                .getRawSubscriber_confirmation_mail_subject().replace(
                    "${portal_url}", self.portal_url.strip('http://'))
            confirmation_url = self.portal_url + '/confirm-subscriber?hkey=' +\
                str(hashkey)
            msg_text = newsletter_container\
                .getRawSubscriber_confirmation_mail_text().replace(
                    "${newsletter_title}", newsletter_container.Title())
            msg_text = msg_text.replace("${subscriber_email}", subscriber)
            msg_text = msg_text.replace(
                "${confirmation_url}", confirmation_url)
            msg_sender = self.portal.getProperty('email_from_address')
            msg_receiver = subscriber
            msg = MIMEText(msg_text)
            msg['To'] = msg_receiver
            msg['From'] = msg_sender
            msg['Subject'] = msg_subject
            # msg.epilogue   = ''
            self.portal.MailHost.send(msg.as_string())
            messages.addStatusMessage(_("Your email has been registered. \
                A confirmation email was sent to your address. Please check \
                your inbox and click on the link in the email in order to \
                confirm your subscription."), "info")
        self.request.response.redirect(newsletter_container.absolute_url())

    def confirm_subscriber(self):
        hashkey = self.request.get('hkey')
        enl_registration_tool = queryUtility(
            IENLRegistrationTool, 'enl_registration_tool')
        regdataobj = enl_registration_tool.get(hashkey)
        messages = IStatusMessage(self.request)
        if regdataobj:
            easynewsletter = self.portal.restrictedTraverse(
                regdataobj.path_to_easynewsletter)
            valid_email, error_code = easynewsletter.addSubscriber(
                regdataobj.subscriber, regdataobj.fullname,
                regdataobj.organization, regdataobj.salutation)
            if valid_email:
                # now delete the regobj
                del enl_registration_tool[hashkey]
                messages.addStatusMessage(
                    _("Your subscription was successfully confirmed."), "info")
            else:
                messages.addStatusMessage(MESSAGE_CODE[error_code], "error")
            return self.request.response.redirect(
                easynewsletter.absolute_url())
        else:
            messages.addStatusMessage(
                _("Please enter a valid email address."), "error")
        return self.request.response.redirect(self.portal.absolute_url())

    def _requestReset(self, userid):
        """Ask the system to start the password reset procedure for
        user 'userid'.

        Returns a dictionary with the random string that must be
        used to reset the password in 'randomstring', the expiration date
        as a DateTime in 'expires', and the userid (for convenience) in
        'userid'.
        # taken from Products.PasswordResetTool but without getValidUser check!
        """
        pwrtool = getToolByName(self.context, 'portal_password_reset')
        randomstring = pwrtool.uniqueString(userid)
        expiry = pwrtool.expirationDate()
        pwrtool._requests[randomstring] = (userid, expiry)
        # clear out untouched records > 10 days old this is a cheap sort of
        # automatic clearing
        pwrtool.clearExpired(10)
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


class UnsubscribeView(BrowserView):

    def __call__(self):
        self.newsletter_url = self.context.absolute_url()
        subscriber = self.request.get('subscriber')
        if subscriber:
            self.send_unsubscribe_email(subscriber)
            return self.request.response.redirect(
                self.newsletter_url)
        else:
            self.form_action = self.newsletter_url + '/unsubscribe'
            return self.index()

    def send_unsubscribe_email(self, subscriber):
        newsletter = self.context
        catalog = getToolByName(self.context, "portal_catalog")
        query = {}
        query["portal_type"] = "ENLSubscriber"
        query["email"] = subscriber
        owner = newsletter.getWrappedOwner()
        newSecurityManager(newsletter, owner)
        results = catalog(query)
        messages = IStatusMessage(self.request)
        if results:
            subscriber_obj = results[0].getObject()
            unsubscribe_url = self.newsletter_url +\
                '/unsubscribe?subscriber=' + subscriber_obj.UID()
            msg_text = """%s: %s""" % (
                newsletter.getUnsubscribe_string(), unsubscribe_url)
            api.portal.send_email(
                recipient=subscriber,
                sender=self.context.email_from_address,
                subject=_(u"confirm newsletter unsubscription"),
                body=msg_text,
            )
            messages.addStatusMessage(
                _("We send you an email, please confirm this unsubscription."),
                "info")
        else:
            messages.addStatusMessage(
                _("Your email address could not be found in subscribers."),
                "error")

    def unsubscribe(self):
        """
        """

        alsoProvides(self.request, IDisableCSRFProtection)
        putils = getToolByName(self.context, "plone_utils")
        catalog = getToolByName(self.context, "reference_catalog")
        uid = self.request.get("subscriber")

        subscriber = catalog.lookupObject(uid)
        if subscriber is None:
            putils.addPortalMessage(_("An error occured"), "error")
        else:
            newsletter = self.context
            # We do the deletion as the owner of the newsletter object
            # so that this is possible without login.
            owner = newsletter.getWrappedOwner()
            newSecurityManager(newsletter, owner)
            del newsletter[subscriber.id]
            putils.addPortalMessage(_("You have been unsubscribed."))

        return self.request.response.redirect(
            api.portal.get_navigation_root(self).absolute_url())
