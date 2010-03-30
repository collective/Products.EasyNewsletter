from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart

from Products.CMFCore.utils import getToolByName

from Products.EasyNewsletter import _

def subscriberAdded(context, event):
    """ send confirmation email """
    newsletter = context.aq_parent
    subscriber = context
    
    # Send confirmation mail
    sender_name = newsletter.getSenderName()
    sender_email = newsletter.getSenderEmail()
    portal = newsletter.portal_url.getPortalObject()
    confirmLink = "%s/confirm-subscription?form.email=%s&form.confirmCode=%s" % \
        (newsletter.absolute_url(), subscriber.getEmail(), subscriber.UID())

    text = newsletter.restrictedTraverse('@@confirm-mail')(\
        newsletter_title=newsletter.Title(),
        newsletter_url=newsletter.absolute_url(),
        confirm_code=subscriber.UID(),
        confirm_link=confirmLink,
        sender_name=sender_name,
        portal_url=portal.absolute_url(),
        portal_title=portal.Title() 
        )

    if sender_name:
        from_header = "%s <%s>" % (sender_name, sender_email)
    else:
        from_header = sender_email

    mail = MIMEMultipart("alternative")
    mail['From'] = from_header
    mail['To'] = subscriber.getEmail()
    mail['Subject'] = _("Confirm newsletter subscription")
    
    props = getToolByName(context, "portal_properties").site_properties
    charset = props.getProperty("default_charset") 

    text_plain = context.portal_transforms.convert('html_to_text', text).getData()
    text_part = MIMEText(text_plain, "plain", charset)
    mail.attach(text_part)

    html_part = MIMEMultipart("related")
    html_part['Content-Transfer-Encoding'] = 'quoted-printable'
    html_text = MIMEText(text, "html", charset)
    html_part.attach(html_text)
    mail.attach(html_part)

    context.MailHost.send(mail.as_string())

