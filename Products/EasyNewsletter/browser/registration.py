import OFS
import re

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from zope.component import queryUtility
#from zope.interface import implements

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

from Products.EasyNewsletter.interfaces import IENLRegistrationTool
from Products.EasyNewsletter.config import MESSAGE_CODE

class SubscriberView(BrowserView):
    """
    """

    @property
    def portal(self):
        return queryUtility(ISiteRoot)

    @property
    def portal_url(self):
        return self.portal.portal_url()

    def register_subscriber(self):
        """
        """
        subscriber = self.request.get("subscriber")
        fullname = self.request.get("fullname", "")
        path_to_easynewsletter = self.request.get("newsletter")
        # remove leading slash from paths like: /mynewsletter
        path_to_easynewsletter = path_to_easynewsletter.strip('/')
        newsletter_container = self.portal.restrictedTraverse(path_to_easynewsletter)
        if not subscriber:
            self.portal.plone_utils.addPortalMessage(MESSAGE_CODE["invalid_email"], "error")
            return self.request.response.redirect(newsletter_container.absolute_url())
        from Products.validation.validators.BaseValidators import EMAIL_RE
        EMAIL_RE = "^" + EMAIL_RE
        mo = re.search(EMAIL_RE, subscriber)
        if not mo: 
            self.portal.plone_utils.addPortalMessage(MESSAGE_CODE["invalid_email"], "error")
            return self.request.response.redirect(newsletter_container.absolute_url())
        if subscriber in newsletter_container.objectIds(): 
            self.portal.plone_utils.addPortalMessage(MESSAGE_CODE["email_exists"], "error")
            return self.request.response.redirect(newsletter_container.absolute_url())
        subscriber_data = {}
        subscriber_data["subscriber"] = subscriber
        subscriber_data["fullname"] = fullname
        subscriber_data["path_to_easynewsletter"] = path_to_easynewsletter

        # use password reset tool to create a hash
        pwr_data = self._requestReset(subscriber)
        hashkey = pwr_data['randomstring']
        enl_registration_tool = queryUtility(IENLRegistrationTool,'enl_registration_tool')
        if hashkey not in enl_registration_tool.objectIds():
            enl_registration_tool[hashkey] = RegistrationData(hashkey, **subscriber_data)
            msg_subject = newsletter_container.getRawSubscriber_confirmation_mail_subject().replace(
                "${portal_url}", self.portal.absolute_url().strip('http://')
            )
            confirmation_url = self.portal.absolute_url() + '/confirm-subscriber?hkey=' + str(hashkey)
            msg_text = newsletter_container.getRawSubscriber_confirmation_mail_text().replace("${newsletter_title}", newsletter_container.Title())
            msg_text = msg_text.replace("${subscriber_email}", subscriber)
            msg_text = msg_text.replace("${confirmation_url}", confirmation_url)
            msg_sender = self.portal.getProperty('email_from_address')
            msg_receiver = subscriber 
            msg = MIMEText(msg_text)
            msg['To']= msg_receiver
            msg['From'] = msg_sender
            msg['Subject'] = msg_subject
            #msg.epilogue   = ''
            self.portal.MailHost.send(msg.as_string())
            self.portal.plone_utils.addPortalMessage(MESSAGE_CODE["email_added"])
        self.request.response.redirect(newsletter_container.absolute_url())

    def confirm_subscriber(self):
        hashkey = self.request.get('hkey')
        enl_registration_tool = queryUtility(IENLRegistrationTool,'enl_registration_tool')
        regdataobj = enl_registration_tool.get(hashkey)
        if regdataobj:
            easynewsletter = self.portal.restrictedTraverse(regdataobj.path_to_easynewsletter)
            valid_email, error_code = easynewsletter.addSubscriber(regdataobj.subscriber, regdataobj.fullname)
            if valid_email:
                # now delete the regobj
                del enl_registration_tool[hashkey]
                self.portal.plone_utils.addPortalMessage(MESSAGE_CODE[error_code])
            else:
                self.portal.plone_utils.addPortalMessage(MESSAGE_CODE[error_code], "error")
        else:
            self.portal.plone_utils.addPortalMessage(MESSAGE_CODE["invalid_hashkey"], "error")
        return self.request.response.redirect(easynewsletter.absolute_url())


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
