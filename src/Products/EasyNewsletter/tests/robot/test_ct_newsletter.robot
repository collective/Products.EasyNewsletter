# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s Products.EasyNewsletter -t test_newsletter.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src Products.EasyNewsletter.testing.PRODUCTS_EASYNEWSLETTER_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/Products/EasyNewsletter/tests/robot/test_newsletter.robot
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

Scenario: As a site administrator I can add a Newsletter
  Given a logged-in site administrator
    and an add Newsletter form
   When I type 'My Newsletter' into the title field
    and I submit the form
   Then a Newsletter with the title 'My Newsletter' has been created

Scenario: As a site administrator I can view a Newsletter
  Given a logged-in site administrator
    and a Newsletter 'My Newsletter'
   When I go to the Newsletter view
   Then I can see the Newsletter title 'My Newsletter'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Newsletter form
  Go To  ${PLONE_URL}/++add++Newsletter

a Newsletter 'My Newsletter'
  Create content  type=Newsletter  id=my-newsletter  title=My Newsletter

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Newsletter view
  Go To  ${PLONE_URL}/my-newsletter
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Newsletter with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Newsletter title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
