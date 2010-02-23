from Acquisition import aq_inner

from zope import interface
from zope import schema
from zope.formlib import form
from zope.schema import ValidationError

from Products.CMFDefault.exceptions import EmailAddressInvalid
from Products.CMFDefault.utils import checkEmailAddress
from Products.Five.formlib import formbase
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.statusmessages.interfaces import IStatusMessage

from Products.EasyNewsletter import _

def validateaddress(value):
    try:  
        checkEmailAddress(value)
    except EmailAddressInvalid:
        raise InvalidEmailAddress(value)   
    return True
    
class InvalidEmailAddress(ValidationError):
    "This is not a valid e-mail address"

class IConfirmSubscriptionForm(interface.Interface):
    """ 
    """
    email = schema.TextLine(title=_(u"email_field_title", default="Email address"),
                            required=True,
                            constraint=validateaddress)
    confirmCode = schema.TextLine(title=_(u"confirmcode_field_title", default="Confirmation code"),
                            required=True)
       
class ConfirmSubscriptionForm(formbase.PageForm):
    """ Confirm form for subscriber
    """
    label = _(u"confirm_subscription_form_label",
              default="Confirm newsletter subscription")
    description = _(u"confirm_subscription_form_description",
                    default="We have received a request for subscription of your email address "
                    "to this newsletter.  To confirm that you want to receive the newsletter "
                    "enter your e-mail address together with the confirm code from the "
                    "confirmation mail.")

    form_fields = form.FormFields(IConfirmSubscriptionForm)

    def _getSubscriber(self, UID):
        context = aq_inner(self.context)
         
        brains = ZCatalog.searchResults(context.portal_catalog, None, UID=UID)

        if brains:
            return brains[0]

    @form.action(_(u"Confirm"))
    def action_submit(self, action, data):
        context = aq_inner(self.context)
        subscriber = self._getSubscriber(data['confirmCode'])

        try:
            # Unauthorized to access a subscriber anonymously, so try to activate
            # this subscriber thru script with manager proxy role.
            activated = context.activate_subscriber(subscriber, data['email'])
        except:
            IStatusMessage(self.request).addStatusMessage(\
                _(u"subscription_form_not_found",
                  default="E-mail address not found or wrong confirmation code."), type="error")
         
            self.request.response.redirect('confirm-subscription?form.email=%s' % data['email'])
        else:
            if activated:
                IStatusMessage(self.request).addStatusMessage(\
                    _(u"subscription_form_confirmed",
                      default="E-mail confirmed for this newsletter."), type="info")
            else:
                IStatusMessage(self.request).addStatusMessage(\
                    _(u"subscription_form_already_confirmed",
                      default="E-mail already confirmed for this newsletter."), type="info")
                self.request.response.redirect(context.absolute_url())