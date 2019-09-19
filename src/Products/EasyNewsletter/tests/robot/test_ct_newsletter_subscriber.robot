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
    and an add Newsletter form
   When I type 'My Newsletter Subscriber' into the title field
    and I submit the form
   Then a Newsletter Subscriber with the title 'My Newsletter Subscriber' has been created

Scenario: As a site administrator I can view a Newsletter Subscriber
  Given a logged-in site administrator
    and a Newsletter Subscriber 'My Newsletter Subscriber'
   When I go to the Newsletter Subscriber view
   Then I can see the Newsletter Subscriber title 'My Newsletter Subscriber'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Newsletter form
  Go To  ${PLONE_URL}/++add++Newsletter

a Newsletter Subscriber 'My Newsletter Subscriber'
  Create content  type=Newsletter  id=my-newsletter_subscriber  title=My Newsletter Subscriber

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Newsletter Subscriber view
  Go To  ${PLONE_URL}/my-newsletter_subscriber
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Newsletter Subscriber with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Newsletter Subscriber title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
