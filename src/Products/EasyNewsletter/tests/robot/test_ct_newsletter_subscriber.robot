# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s Products.EasyNewsletter -t test_newsletter_subscriber.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src Products.EasyNewsletter.testing.PRODUCTS_EASYNEWSLETTER_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/Products/EasyNewsletter/tests/robot/test_newsletter_subscriber.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


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

a Newsletter with a Subscriber 'subscriber@example.com'
  ${newsletter_uid}=  Create content  type=Newsletter  id=my-newsletter  title=My Newsletter  sender_email=sender@example.com  sender_name=Test Sender  test_email=test@example.com
  Create content  type=Newsletter Subscriber  id=my-subscriber  email=subscriber@example.com  container=${newsletter_uid}

# --- WHEN -------------------------------------------------------------------

I type '${email}' into the email field
  Input Text  name=form.widgets.email  ${email}

I submit the form
  Press Keys  name=form.widgets.email  TAB
  Click Button  Save

I go to the Newsletter Subscriber view
  Go To  ${PLONE_URL}/my-newsletter/my-subscriber
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Newsletter Subscriber with email '${email}' has been created
  Wait until page contains  Site Map
  Page should contain  ${email}
  Page should contain  Item created

I can see the Newsletter Subscriber email '${email}'
  Wait until page contains  Site Map
  Page should contain  ${email}
