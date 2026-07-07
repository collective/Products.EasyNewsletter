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
#  $ bin/test -s Products.EasyNewsletter -t test_ct_newsletter_issue.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src Products.EasyNewsletter.testing.PRODUCTS_EASYNEWSLETTER_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/Products/EasyNewsletter/tests/robot/test_ct_newsletter_issue.robot
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

Scenario: As a site administrator I can add a Newsletter Issue
  Given a logged-in site administrator
    and a Newsletter 'My Newsletter'
    and an add Newsletter Issue form
   When I type 'My Newsletter Issue' into the title field
    and I submit the form
   Then a Newsletter Issue with the title 'My Newsletter Issue' has been created

Scenario: As a site administrator I can view a Newsletter Issue
  Given a logged-in site administrator
    and a Newsletter with an Issue 'My Newsletter Issue'
   When I go to the Newsletter Issue view
   Then I can see the Newsletter Issue title 'My Newsletter Issue'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

a Newsletter 'My Newsletter'
  Create content  type=Newsletter  id=my-newsletter  title=My Newsletter  sender_email=sender@example.com  sender_name=Test Sender  test_email=test@example.com

an add Newsletter Issue form
  Go To  ${PLONE_URL}/my-newsletter/++add++Newsletter Issue
  Wait For Condition  Classes  //body  contains  patterns-loaded

a Newsletter with an Issue 'My Newsletter Issue'
  ${newsletter_uid}=  Create content  type=Newsletter  id=my-newsletter  title=My Newsletter  sender_email=sender@example.com  sender_name=Test Sender  test_email=test@example.com
  Create content  type=Newsletter Issue  id=my-newsletter-issue  title=My Newsletter Issue  container=${newsletter_uid}

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Type Text  //input[@name="form.widgets.IBasic.title"]  ${title}

I submit the form
  Click  //button[@name="form.buttons.save"]

I go to the Newsletter Issue view
  Go To  ${PLONE_URL}/my-newsletter/my-newsletter-issue


# --- THEN -------------------------------------------------------------------

a Newsletter Issue with the title '${title}' has been created
  Get Text  //body  contains  ${title}
  Get Text  //body  contains  Item created

I can see the Newsletter Issue title '${title}'
  Get Text  //body  contains  ${title}
