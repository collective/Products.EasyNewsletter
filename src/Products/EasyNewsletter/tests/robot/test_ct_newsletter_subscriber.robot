# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# These tests use the Playwright based robotframework-browser library
# (plone/app/robotframework/browser.robot). Before running them once, the
# Playwright node dependencies and browser binaries must be installed:
#
#  $ uv run rfbrowser init
#
# Run this robot test stand-alone:
#
#  $ bin/test -s Products.EasyNewsletter -t test_ct_newsletter_subscriber.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src Products.EasyNewsletter.testing.PRODUCTS_EASYNEWSLETTER_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/Products/EasyNewsletter/tests/robot/test_ct_newsletter_subscriber.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/browser.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Plone Test Setup
Test Teardown  Plone Test Teardown


*** Test Cases ***************************************************************

Scenario: As a site administrator I can add a Newsletter Subscriber
  Given a logged-in site administrator
    and a Newsletter 'My Newsletter'
    and an add Newsletter Subscriber form
   When I type 'subscriber@example.com' into the email field
    and I submit the form
   Then a Newsletter Subscriber with email 'subscriber@example.com' has been created

Scenario: As a site administrator I can view a Newsletter Subscriber
  Given a logged-in site administrator
    and a Newsletter with a Subscriber 'subscriber@example.com'
   When I go to the Newsletter Subscriber view
   Then I can see the Newsletter Subscriber email 'subscriber@example.com'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

a Newsletter 'My Newsletter'
  Create content  type=Newsletter  id=my-newsletter  title=My Newsletter  sender_email=sender@example.com  sender_name=Test Sender  test_email=test@example.com

an add Newsletter Subscriber form
  Go To  ${PLONE_URL}/my-newsletter/++add++Newsletter Subscriber
  Wait For Condition  Classes  //body  contains  patterns-loaded

a Newsletter with a Subscriber 'subscriber@example.com'
  ${newsletter_uid}=  Create content  type=Newsletter  id=my-newsletter  title=My Newsletter  sender_email=sender@example.com  sender_name=Test Sender  test_email=test@example.com
  Create content  type=Newsletter Subscriber  id=my-subscriber  email=subscriber@example.com  container=${newsletter_uid}

# --- WHEN -------------------------------------------------------------------

I type '${email}' into the email field
  Type Text  //input[@name="form.widgets.email"]  ${email}

I submit the form
  Press Keys  //input[@name="form.widgets.email"]  Tab
  Click  //button[@name="form.buttons.save"]

I go to the Newsletter Subscriber view
  Go To  ${PLONE_URL}/my-newsletter/my-subscriber


# --- THEN -------------------------------------------------------------------

a Newsletter Subscriber with email '${email}' has been created
  Get Text  //body  contains  ${email}
  Get Text  //body  contains  Item created

I can see the Newsletter Subscriber email '${email}'
  Get Text  //body  contains  ${email}
