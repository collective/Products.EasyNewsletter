# -*- coding: utf-8 -*-
from AccessControl.SecurityManagement import newSecurityManager
from Acquisition import aq_inner
from email_validator import EmailNotValidError, validate_email
from logging import getLogger
from plone import api
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFCore.utils import getToolByName
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _  # noqa
from Products.EasyNewsletter.config import MESSAGE_CODE
from Products.EasyNewsletter.content.newsletter import INewsletter
from Products.EasyNewsletter.content.newsletter_subscriber import INewsletterSubscriber
from Products.EasyNewsletter.interfaces import IENLRegistrationTool
from Products.EasyNewsletter.utils.base import execute_under_special_role
from Products.EasyNewsletter.utils.mail import get_portal_mail_settings
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zExceptions import BadRequest
from zope.component import getMultiAdapter, queryUtility
from zope.interface import alsoProvides

import emails
import OFS


try:
    from plone import protect
except ImportError:
    # BBB for old plone.protect, default until at least Plone 4.3.7.
    protect = None


logger = getLogger("ENL Registration")


class SubscriberView(BrowserView):
    """
    """

    def _msg_redirect(self, newsletter):
        """To also display messages for anon users
        """
        if api.user.is_anonymous():
            return self.request.response.redirect(self.context.absolute_url())
        else:
            self.request.response.redirect(newsletter.absolute_url())

    def portal_state(self):
        context = aq_inner(self.context)
        return getMultiAdapter((context, self.request), name=u"plone_portal_state")

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
        messages = IStatusMessage(self.request)
        path_to_easynewsletter = self.request.get("newsletter")
        # remove leading slash from paths like: /mynewsletter
        path_to_easynewsletter = path_to_easynewsletter.strip("/")
        newsletter_container = self.portal.unrestrictedTraverse(path_to_easynewsletter)

        subscriber = self.request.get("subscriber")
        try:
            validate_email(subscriber)
        except EmailNotValidError as e:
            messages.addStatusMessage(_("Please enter a valid email address.\n{0}".format(e)), "error")
            return self._msg_redirect(newsletter_container)

        lastname = self.request.get("name", "")
        firstname = self.request.get("firstname", "")
        name_prefix = self.request.get("name_prefix", "")
        portal_state = getMultiAdapter(
            (self.context.aq_inner, self.request), name=u"plone_portal_state"
        )
        current_language = portal_state.language()
        nl_language = self.request.get("nl_language", current_language)
        salutation = self.request.get("salutation", "")
        organization = self.request.get("organization", "")

        norm = queryUtility(IIDNormalizer)
        normalized_subscriber = norm.normalize(subscriber)
        if normalized_subscriber in newsletter_container.objectIds():
            messages.addStatusMessage(
                _("Your email address is already registered."), "error"
            )
            return self._msg_redirect(newsletter_container)
        subscriber_data = {}
        subscriber_data["subscriber"] = subscriber
        subscriber_data["lastname"] = lastname
        subscriber_data["firstname"] = firstname
        subscriber_data["name_prefix"] = name_prefix
        subscriber_data["nl_language"] = nl_language
        subscriber_data["salutation"] = salutation
        subscriber_data["organization"] = organization
        subscriber_data["path_to_easynewsletter"] = path_to_easynewsletter

        # use password reset tool to create a hash
        pwr_data = self._requestReset(subscriber)
        hashkey = pwr_data["randomstring"]
        enl_registration_tool = queryUtility(
            IENLRegistrationTool, "enl_registration_tool"
        )
        if hashkey not in enl_registration_tool.objectIds():
            enl_registration_tool[hashkey] = RegistrationData(
                hashkey, **subscriber_data
            )
            msg_subject = newsletter_container.subscriber_confirmation_mail_subject.replace(
                "${portal_url}", self.portal_url.strip("http://")
            )
            confirmation_url = (
                self.portal_url + "/confirm-subscriber?hkey=" + str(hashkey)
            )
            confirmation_url = protect.utils.addTokenToUrl(confirmation_url)
            msg_text = newsletter_container.subscriber_confirmation_mail_text.replace(
                "${newsletter_title}", newsletter_container.title
            )
            msg_text = msg_text.replace("${subscriber_email}", subscriber)
            msg_text = msg_text.replace("${confirmation_url}", confirmation_url)
            settings = get_portal_mail_settings()
            msg_sender = settings.email_from_address
            msg_receiver = subscriber
            msg = emails.Message(
                text=msg_text,
                subject=msg_subject,
                mail_from=msg_sender,
                mail_to=msg_receiver,
            )
            self.portal.MailHost.send(msg.as_string())

            messages.addStatusMessage(
                _(
                    "Your email has been registered. \
                A confirmation email was sent to your address. Please check \
                your inbox and click on the link in the email in order to \
                confirm your subscription."
                ),
                "info",
            )
            return self._msg_redirect(newsletter_container)

    def confirm_subscriber(self):
        hashkey = self.request.get("hkey")
        enl_registration_tool = queryUtility(
            IENLRegistrationTool, "enl_registration_tool"
        )
        regdataobj = enl_registration_tool.get(hashkey)
        messages = IStatusMessage(self.request)
        if regdataobj:
            portal = api.portal.get()
            easynewsletter = portal.unrestrictedTraverse(
                regdataobj.path_to_easynewsletter
            )
            email = regdataobj.subscriber
            plone_utils = api.portal.get_tool(name="plone_utils")
            subscriber_id = plone_utils.normalizeString(email)
            try:
                execute_under_special_role(
                    portal,
                    "Contributor",
                    api.content.create,
                    type="Newsletter Subscriber",
                    id=subscriber_id,
                    language=self.context.language,
                    email=email,
                    firstname=regdataobj.firstname,
                    lastname=regdataobj.lastname,
                    name_prefix=regdataobj.name_prefix,
                    # nl_language=regdataobj.nl_language,
                    organization=regdataobj.organization,
                    salutation=regdataobj.salutation,
                    container=easynewsletter,
                )
            except BadRequest:
                error_code = u"email_exists"
                messages.addStatusMessage(MESSAGE_CODE[error_code], "error")
            else:
                # now delete the regobj
                del enl_registration_tool[hashkey]
                messages.addStatusMessage(
                    _("Your subscription was successfully confirmed."), "info"
                )
            return self._msg_redirect(easynewsletter)
        else:
            messages.addStatusMessage(_("Please enter a valid email address."), "error")
        return self.request.response.redirect(self.context.absolute_url())

    def _requestReset(self, userid):  # noqa
        """Ask the system to start the password reset procedure for
        user 'userid'.

        Returns a dictionary with the random string that must be
        used to reset the password in 'randomstring', the expiration date
        as a DateTime in 'expires', and the userid (for convenience) in
        'userid'.
        # taken from Products.PasswordResetTool but without getValidUser check!
        """
        pwrtool = getToolByName(self.context, "portal_password_reset")
        randomstring = pwrtool.uniqueString(userid)
        expiry = pwrtool.expirationDate()
        pwrtool._requests[randomstring] = (userid, expiry)
        # clear out untouched records > 10 days old this is a cheap sort of
        # automatic clearing
        pwrtool.clearExpired(10)
        pwrtool._p_changed = 1
        retval = {}
        retval["randomstring"] = randomstring
        retval["expires"] = expiry
        retval["userid"] = userid
        return retval


class RegistrationData(OFS.SimpleItem.Item):
    """ holds data from ENL registration form
    """

    def __init__(self, id, **kw):
        self.id = id
        for key, value in kw.items():
            setattr(self, key, value)
        # super(RegistrationData, self).__init__()

    @property
    def title(self):
        return "%s - %s" % (" ".join([self.firstname, self.lastname]), self.subscriber)


class UnsubscribeView(BrowserView):
    def __call__(self):
        self.newsletter_url = self.context.absolute_url()
        subscriber = self.request.get("subscriber")

        if subscriber:
            self.send_unsubscribe_email(subscriber)
            return self.request.response.redirect(self.newsletter_url)
        else:
            self.form_action = self.newsletter_url + "/unsubscribe"
            return self.index()

    def send_unsubscribe_email(self, subscriber):
        newsletter = self.context
        catalog = getToolByName(self.context, "portal_catalog")
        query = {}
        query["portal_type"] = "Newsletter Subscriber"
        query["email"] = subscriber
        results = catalog.unrestrictedSearchResults(query)
        messages = IStatusMessage(self.request)
        if results:
            subscriber_brain = results[0]
            unsubscribe_url = (
                self.newsletter_url + "/unsubscribe?subscriber=" + subscriber_brain.UID
            )
            msg_text = """%s: %s""" % (newsletter.unsubscribe_string, unsubscribe_url)
            settings = get_portal_mail_settings()
            api.portal.send_email(
                recipient=subscriber,
                sender=settings.email_from_address,
                subject=_(u"confirm newsletter unsubscription"),
                body=msg_text,
            )
            messages.addStatusMessage(
                _("We send you an email, please confirm this unsubscription."), "info"
            )
        else:
            # todo: write an extra error msg if a plone user wants to
            # unsubscribe himself
            messages.addStatusMessage(
                _("Your email address could not be found in subscribers."), "error"
            )

    def unsubscribe(self):
        """
        """
        if protect is not None:
            alsoProvides(self.request, protect.interfaces.IDisableCSRFProtection)
        putils = getToolByName(self.context, "plone_utils")
        uid = self.request.get("subscriber")

        newsletter = self.context
        if not INewsletter.providedBy(newsletter):
            putils.addPortalMessage(
                _("Please use the correct unsubscribe url!"), "error"
            )
            return self.request.response.redirect(
                api.portal.get_navigation_root(self).absolute_url()
            )

        # We do the deletion as the owner of the newsletter object
        # so that this is possible without login.
        owner = newsletter.getWrappedOwner()
        newSecurityManager(newsletter, owner)
        subscriber = api.content.get(UID=uid)
        if subscriber is None or not INewsletterSubscriber.providedBy(subscriber):
            putils.addPortalMessage(_("An error occured"), "error")
        else:
            del newsletter[subscriber.id]
            putils.addPortalMessage(_("You have been unsubscribed."))

        return self.request.response.redirect(
            api.portal.get_navigation_root(self).absolute_url()
        )
