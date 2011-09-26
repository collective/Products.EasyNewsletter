import re
from Products.Archetypes.atapi import DisplayList
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _


PROJECTNAME = "EasyNewsletter"


PLACEHOLDERS = ["UNSUBSCRIBE", "SUBSCRIBER_SALUTATION"]


SALUTATION = DisplayList((
    ('', _(u"label_choose_saluation", "Choose salutation...")),
    ("ms", _(u"label_salutation_ms", "Ms.")),
    ("mr", _(u"label_salutation_mr", "Mr.")),
))


EMAIL_RE = re.compile(r"(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)", re.IGNORECASE)


DEFAULT_TEMPLATE = """
<tal:block tal:repeat="object context/queryCatalog">
    <h1 tal:content="object/Title">Title</h1>

    <p>
        <span tal:content="object/Description">Description</span>
    </p>
    <p>
        <a tal:attributes="href object/getURL">Please read on.</a>
    </p>
</tal:block>

<tal:block tal:repeat="subtopic context/getSubTopics">
    <h1 tal:content="subtopic/Title">Title</h1>

    <tal:block tal:repeat="object subtopic/queryCatalog">
        <h2 tal:content="object/Title">Title</h2>

        <p>
            <span tal:content="object/Description">Description</span>
        </p>
        <p>
            <a tal:attributes="href object/getURL">Please read on.</a>
        </p>
    </tal:block>
</tal:block>
"""


DEFAULT_OUT_TEMPLATE_PT = """<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title><tal:title content="context/Title" /></title>
<style type="text/css">

</style>
</head>
<body>
    <!-- this is the header of the newsletter -->
    <div class="header">
        <span tal:replace="structure context/getHeader" />
    </div>

    <!-- this is the main text of the newsletter -->
    <div class="body-text">
        <span tal:replace="structure context/getText" />
        <tal:def tal:define="files context/getFiles">
            <dl id="file-attachments" tal:condition="files">
                <tal:loop repeat="file files">
                    <dt>
                        <a tal:attributes="href file/getURL" tal:content="file/Title" />
                    </dt>
                    <dd tal:content="file/Description" />
                </tal:loop>
            </dl>
        </tal:def>
    </div>

    <!-- this is the footer of the newsletter -->
    <div class="footer">
        <span tal:replace="structure context/getFooter" />
    </div>
</body>
</html>"""


DEFAULT_SUBSCRIBER_CONFIRMATION_MAIL_SUBJECT = """Confirm your subscription on ${portal_url}"""

DEFAULT_SUBSCRIBER_CONFIRMATION_MAIL_TEXT = """You asked to subscribe to ${newsletter_title}.\n\n
Your email is: ${subscriber_email}\n\n
Please click on the link to confirm your subscription: \n\n
${confirmation_url}"""


DEFAULT_SUBSCRIBER_ALREADY_MAIL_SUBJECT = """You are already subscribed on ${portal_url}"""

DEFAULT_SUBSCRIBER_ALREADY_MAIL_TEXT = """You asked to subscribe to ${newsletter_title}.\n\n
Your email is: ${subscriber_email}\n\n
You are already subscribed."""


DEFAULT_UNSUBSCRIBER_CONFIRMATION_MAIL_SUBJECT = """Confirm your unsubscription on ${portal_url}"""

DEFAULT_UNSUBSCRIBER_CONFIRMATION_MAIL_TEXT = """You asked to unsubscribe to ${newsletter_title}.\n\n
Your email is: ${subscriber_email}\n\n
Please click on the link to confirm your unsubscription: \n\n
${confirmation_url}"""


DEFAULT_UNSUBSCRIBER_NOT_MAIL_SUBJECT = """You are not subscribed on ${portal_url}"""

DEFAULT_UNSUBSCRIBER_NOT_MAIL_TEXT = """You asked to unsubscribe to ${newsletter_title}.\n\n
Your email is: ${subscriber_email}\n\n
You are not subscribed."""
