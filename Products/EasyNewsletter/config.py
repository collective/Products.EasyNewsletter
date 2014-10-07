# -*- coding: utf-8 -*-
# flake8: noqa
# from zope.i18n import translate
from Products.Archetypes.atapi import DisplayList
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _
import re

PROJECTNAME = "EasyNewsletter"


PLACEHOLDERS = ["UNSUBSCRIBE", "SUBSCRIBER_SALUTATION"]


SALUTATION = DisplayList((
    ('', _(u"label_choose_saluation", "Choose salutation...")),
    ("ms", _(u"label_salutation_ms", "Ms.")),
    ("mr", _(u"label_salutation_mr", "Mr.")),
))


MESSAGE_CODE = {
    "email_added": _(
        u"email_added",
        default=u"Your email has been registered. A confirmation email was"
                u" sent to your address. Please check your inbox and click "
                u" on the link in the email in order to confirm your"
                u" subscription."
    ),
    "invalid_email": _(
        u"invalid_email", default=u"Please enter a valid email address."),
    "email_exists": _(
        u"email_exists", default=u"Your email address is already registered."),
    "invalid_hashkey": _(
        u"invalid_hashkey", default=u"Please enter a valid email address."),
    "subscription_confirmed": _(
        u"subscription_confirmed",
        default=u"Your subscription was successfully confirmed."),
    }


EMAIL_RE = re.compile(
    r"(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)", re.IGNORECASE)


DEFAULT_TEMPLATE = """\
<table border="0" cellpadding="10" cellspacing="10" width="100%">
<tal:block tal:repeat="object context/queryCatalog"
    i18n:domain="EasyNewsletter">
  <tr>
    <td>
      <h2 class="tileHeadline"><a tal:attributes="href object/getURL"
        tal:content="object/Title">Title</a></h2>
      <p class="tileBody">
        <span tal:content="object/Description">Description</span>
      </p>
      <p class="tileFooter">
        <a tal:attributes="href object/getURL"
            i18n:translate="read_more">Read more</a>&hellip;
      </p>
    </td>
    <td width="164" align="right">
      <tal:image_obj tal:define="item_object object/getObject;">
        <tal:block
            condition="python:object.portal_type in ['Image', 'News Item']">
          <a tal:attributes="href object/getURL">
            <img class="tileImage"
                tal:condition="python:hasattr(item_object, 'tag')"
tal:attributes="src python:object.getURL(relative=1) + '/@@images/image/thumb'"
                />
          </a>
        </tal:block>
      </tal:image_obj>
    </td>
  </tr>
</tal:block>
</table>

<tal:block tal:repeat="subtopic context/getSubTopics">
<table border="0" cellpadding="10" cellspacing="10" width="100%">
  <tr>
    <th>
      <h1 tal:content="subtopic/Title">Title</h1>
    </th>
  </tr>
<tal:blockitems tal:repeat="object subtopic/queryCatalog"
    i18n:domain="EasyNewsletter">
  <tr>
    <td>
      <h2 class="tileHeadline"><a
        tal:attributes="href object/getURL"
        tal:content="object/Title">Title</a></h2>
      <p class="tileBody">
        <span tal:content="object/Description">Description</span>
      </p>
      <p class="tileFooter">
        <a tal:attributes="href object/getURL"
            i18n:translate="read_more">Read more</a>&hellip;
      </p>
    </td>
  </tr>
  <tr>
    <td width="164" align="right">
      <tal:image_obj tal:define="item_object object/getObject;">
        <tal:block
            condition="python:object.portal_type in ['Image', 'News Item']">
        <a tal:attributes="href object/getURL">
          <img class="tileImage"
              tal:condition="python:hasattr(item_object, 'tag')"
tal:attributes="src python:object.getURL(relative=1) + '/@@images/image/thumb'"
              />
        </a>
        </tal:block>
      </tal:image_obj>
    </td>
  </tr>
</tal:blockitems>
</tal:block>"""


DEFAULT_OUT_TEMPLATE_PT = """<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title><tal:title content="context/Title" /></title>
<style type="text/css">
body {
  color: #333 !important;
}
h1, h2, h3, h1 a, h2 a, h3 a {
  color: #979799! important;
}
th, td {
  padding: 0;
}
tileItem {
  display: block;
}
img.tileImage {
  float: right;
  margin: 10px 0 10px 10px !important;
}
.visualClear {
  clear: both;
  display: block;
}
</style>
</head>
<body>
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td>
        <div class="mailonly"
            tal:define="portal_url context/@@plone_portal_state/portal_url">
          <img src="logo.png" />
        </div>
      </td>
    </tr>
    <tr>
      <td height="10px">
        <!-- -->
      </td>
    </tr>
    <tr>
      <td height="1"
        style="background-color: #284d7b; height: 1px;"><!-- --></td>
    </tr>
    <tr>
      <td height="20">
        <!-- -->
      </td>
    </tr>
    <tr>
      <td class="newsletter_link">
        <div class="mailonly">
          <p><a
            tal:attributes="href context/absolute_url"
                >View Newsletter in Web-browser</a></p>
        </div>
      </td>
    </tr>
    <tr>
      <td class="header">
        <!-- this is the header of the newsletter -->
        <span tal:replace="structure context/getHeader" />
        <span
        tal:define="toLocalizedTime nocall:context/@@plone/toLocalizedTime"
tal:replace="structure python:toLocalizedTime(context.modified(), long_format=0)" />
      </td>
    </tr>
    <tr>
      <td class="body">
        <!-- this is the main text of the newsletter -->
        <div class="mailonly">
          <p><span tal:replace="structure context/Description" /></p>
        </div>
        <span tal:replace="structure context/getText" />
        <tal:def tal:define="files context/getFiles">
            <dl id="file-attachments" tal:condition="files">
                <tal:loop repeat="file files">
                    <dt>
                        <a tal:attributes="href file/getURL"
                           tal:content="file/Title" />
                    </dt>
                    <dd tal:content="file/Description" />
                </tal:loop>
            </dl>
        </tal:def>
      </td>
    </tr>
    <tr>
      <td class="footer">
        <!-- this is the footer of the newsletter -->
        <span tal:replace="structure context/getFooter" />
      </td>
    </tr>
  </table>
</body>
</html>"""


DEFAULT_SUBSCRIBER_CONFIRMATION_MAIL_SUBJECT = _(
    u"Confirm your subscription on ${portal_url}"
)

DEFAULT_SUBSCRIBER_CONFIRMATION_MAIL_TEXT = """\
You subscribe to the ${newsletter_title} Newsletter.\n\n
Your registered email is: ${subscriber_email}\n
Please click on the link to confirm your subscription: \n
${confirmation_url}"""
