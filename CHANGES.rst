Changelog
=========


5.0.4 (2021-04-22)
------------------

- Improve iframe reziser handling for online view of newsletter issues. Works now better even if JS is broken. Also disable requireJS for the injected JS.
  [MrTango]

- fix preview_html method/separat preview window view
  [MrTango]


5.0.3 (2021-04-14)
------------------

- Fix image handling in aggregation templates
  [MrTango]


5.0.2 (2021-03-22)
------------------

- Fix wrong redirect urls for error redirects in subscribers-upload form
  [MrTango]


5.0.1 (2021-03-16)
------------------

- Add preview parameter to _render_output_html, which can be used to distinguish preview from email rendering
  [MrTango]


5.0.0 (2021-02-04)
------------------

- use email_validator.validate_email in plone_user vocab, fixes #159
  [MrTango]


5.0.0b3 (2021-02-03)
--------------------

- Fix dublicate text in action buttons on newsletter-subscribers view.
  [MrTango]


5.0.0b2 (2021-02-03)
--------------------

- Don't fail sending process when one email fails
  [thomasmassmann]

- Fix helper method: get_results_from_aggregation_sources, which can be used for a table of contents
  [MrTango]

- Update output_blacksee template with a TOC and some CSS cleanup
  [MrTango]

- Switch from travis to Github-Actions and fix tests
  [MrTango]

- Fixed empty epilog error #162
  [iham]

- Add Newsletter title to the unsubscribe email subject #131
  [MrTango]


5.0.0b1 (2020-03-08)
--------------------

- Add userid to member property dict for plone subscribers.
  [thomasmassmann]

- Add information about sent emails to Newsletter Issue.
  [thomasmassmann]


5.0.0a9 (2019-12-14)
--------------------

- Force immediate sending in MailHost
  [MrTango]

- Add portal messages with send_counter/send_error_counter
  [MrTango]

- Add divers for salutation and make salutation optional in subscriber portlet
  [MrTango]

- Refacture locales/update.py and fix german translations
  [MrTango]


5.0.0a8 (2019-12-12)
--------------------

- Fix unsubscribe url in subscriber portlet
  [MrTango]

- Allow subscribers to not fill-in the Name, when subscribing
  [MrTango]

- Add additional_info field to subscriber portlet, useful for things like terms and conditions
  [MrTango]

- Allow local Plone users and groups to be used as recipients
  [tmassman]


5.0.0a7 (2019-10-09)
--------------------

- Fix subscribers csv download/export (Py3/Py27)
  [MrTango]


5.0.0a6 (2019-10-08)
--------------------

- Improve placeholder docs and implementation, only use lower case placeholders from now on
  [MrTango]

- remove old entries in portal_types registration from uninstall profile
  [MrTango]


5.0.0a5 (2019-10-07)
--------------------

- Add placeholder for calendar_week
  [MrTango]


5.0.0a4 (2019-10-04)
--------------------

- Fix upgrade step 4004
  MrTango


5.0.0a3 (2019-10-04)
--------------------

- Fix MANIFEST after changing package structure
  [MrTango]


5.0.0a2 (2019-10-04)
--------------------

- Fix setup.py by providing z3c.autoinclude entrypoint
  [MrTango]

5.0.0a1 (2019-09-23)
--------------------

- Remove Archetypes from code base and remove Archetypes dependencies
  [MrTango]


4.0.0 (unreleased)
--------------------

- Implement content types in Dexterity instead of Archetypes
  [MrTango]

- Refactored sending and personalization, as well as issuedatafetcher adapter
  [MrTango]

- Implement Plone user/groups sources as behaviors
  [MrTango]

- Implement Collection behavior which supports aggregation templates on each collection
  [MrTango]

- Add modern views for most of the existing once, which plonecli, containing basic tests
  [MrTango]

- Add vocabularies for all Archetypes DisplayLists
  [MrTango]

- Fix unsubscribe_view and add some checks/tests for security
  [MrTango]


3.0.9 (unreleased)
------------------

- Nothing changed yet.


3.0.8 (2019-08-19)
------------------

- Make effectiveDate visible on ENLIssue and use it in Newsletter archive view instead of modified date for sorting
  [MrTango]


3.0.7 (2019-08-15)
------------------

- Allow send action only in draft state to prevent side effects for users.
  [agitator]

- Fix styles for subscriber portlet
  [MrTango]

- fix plone4 setup, by pinning plone.api to recent version
  [MrTango]

- Fix spelling in template
  [MrTango]

- Add plone.protect support to confirm-subscriber view and fix redirect to ENL object
  [MrTango]


3.0.6 (2018-02-18)
------------------

- DisableCSRFProtection for daily issue views, which are triggered by cron
  jobs
  [MrTango]


3.0.5 (2017-11-22)
------------------

- Use same cmf.ReviewPortalContent permission for taskqueue sendout as with standard sendout.
  [agitator]

- Show newsletter toolbar for reviewers.
  [agitator]

- Set effective date after sending an issue.
  [Gagaro]

- Fix subscriber portlet, it now reflects all settings also on addform
  [MrTango]


3.0.4 (2017-09-25)
------------------

- add plone.protect >= 3.1.1 and plone4.csrffixes>=1.1 as dependencies
  [MrTango]


3.0.3 (2017-09-12)
------------------

- Show all placeholders with dummy data in the separate preview window
  [MrTango]


3.0.2 (2017-07-29)
------------------

- Fix iFrameReziser in ENL Issue preview
  [MrTango]


3.0.1 (2017-07-21)
------------------

- Add test and documentation for customizing email personalization in addons.
  [MrTango]


3.0 (2017-07-16)
----------------

- Use globaly unique Content-Id for attached images. This fixes caching issues in some clients.
  [MrTango]

- Fix resolving default salutation
  [MrTango]


3.0b3 (2017-06-13)
------------------

- Just fix broken release on pypi


3.0b2 (2017-06-12)
------------------

- CSV import checks for duplicates based on email and updates existing subscribers.
  [agitator]

- Show newsletter issue preview in iframe
  [agitator]

- Refactured output and aggregation template rendering
  [MrTango]

- no write on read for issue public view anymore
  [MrTango]

- fixed permissions of issue in sent state
  [MrTango]

- refacture daily_issue view to work with new aggregation templates
  [MrTango]

- improved newsletter menu handling
  [agitator]

- Update documentation
  [MrTango]


3.0b1 (2017-05-15)
------------------

- Use new Collections for aggregating content
  [MrTango]

- Provide more and better email tempalte (output and aggregation)
  Templates are based and inspired on: https://github.com/mailchimp/email-blueprints
  [MrTango]

- Added newsletter toolbar and icons for Plone 5
  [agitator]

- A bunch of fixes in order to work better with Plone 5, plone.protect/CSRF protection and also some cleanup.
  [jensens]

- ``collective.taskqueue`` asynchronous send out support added.
  [jensens]

- Made sent issues visible to public
  [agitator]

- Give a redirect with a status message back to the issue page after sending a
  news letter issue directly (without asynchronous queueing), this was broken
  after the zamqp support was added.
  [fredvd]

- Do a transaction.commit() after changing the Issue workflow to 'sending' so
  we are certain another incoming request for sending the issue will see the
  change and fail in direct send mode. (Fixes #83)
  [fredvd]

- Only add IDisableCSRFProtection to the unsubscribe view if the supported
  newer plone.protect is available. Don't force dependency on plone.protect
  3.X
  [fredvd]

- zamqp: removed auto_delete property to keep sending queues on consumer restart
  [agitator]

- Added firstname, lastname and gender to enl_receivers dictionary
  [agitator]

- Added IBeforePersonalizationEvent for customisations
  [jensens]

- Use jinja syntax for template processing
  [jensens]

- Rafactoring of ENLIssue personalization
  [jensens]

- Language independent CSV Header
  [agitator]

- Unsubscribe page works now with plone.protect enabled
  [agitator]

- Changed unsubscribe target link to navigation root, to allow unsubscribe from a private newsletter without showing the login page.
  [agitator]

- Fixed renaming issue on copy_as_draft
  [agitator]

- Fixed usage of inline images from plone.app.contenttypes.
  [agitator]

- Clean up upgrade steps for adding catalog indexes. There's only one method in   setuphandlers now that adds indexes when they not already exist.
  [fredvd]

- Add extra textlines and corresponding translations id's in the drafts,
  masters and templates overview to clarify the difference in usage between
  them.
  [fredvd]

- Update Spanish translation
  [macagua]

- Added more improvements about i18n
  [macagua]

- Supported by v3.x is Plone 4.3.x+ and later.
  [jensens, agitator]

- Added optional queued sendout using ``collective.zamqp``. In order to not
  enqueue twice the workflow goes over a sending state now.
  [jensens]

- Update french translation by adding missing labels
  [mordicusetcubitus]

- Now use site_properties default charset for email subscription confirmation
  Before this was done using us-ascii preventing from displaying properly
  non ascii letters like éàù...
  [mordicusetcubitus]

- Fixed jquery initialization in enl_edithelper.js and make it work again.
  It didn't hide the user selection fields.
  [benniboy]

- Status and error messsages show up for anon users (was broke).
  [benniboy]

- Implemented that subscribers and recipients have a language. This is also
  queable via index and the affecting page templates have been adjusted.
  [benniboy]

- Made a checkbox in the send issue form to exclude all external subscribers.
  [benniboy]

- Split up the send method for better hookability.
  [benniboy]

- Reworked the whole issue workflow. See README.
  [benniboy]

- Added info on several newsletter fields, that changing settings does not
  affect already existing issues for that newsletter.
  [benniboy]

- Fixed enl_edithelper.py work again.
  [benniboy]

- Added 2 new constants to the config.py for hookability and adjusted the
  affected files to look up those constants.
  [benniboy]

- Fixed a subscriber can now unsubscribe himself, if he is not logged in.
  [benniboy]

- Reworked the salutation mapping (prepared for multilingual newsletter)
  [benniboy]

- Added utf-8 headers, sorted imports (plone-style), lines down to 80 chars.
  Unified qa in ``qa.cfg``, enforce more qa rules.
  [jensens]

- Extended subscriber for firstname, lastname and prefix,
  updated csv export and import. Added migration step.
  [agitator]

- Added subscriber to SearchableText index, but excluded from default results.
  [agitator]

- Updated portlet fields, fullname is now "generic" name. Updated portlet options
  to be queried for at subscription time.
  [agitator]

- Marked E-Mail, Salutation and Name as required if present in subscription portlet.
  [agitator]

- Change subscriber search into fulltext search via SearchableText
  [agitator]


2.6.14 (2014-07-10)
-------------------

- Update german translations
  [MrTango]


2.6.13 (2014-06-05)
-------------------

- Added tests for sending images
  [djay]
- Fixed issues with sending images in Plone 4.0-4.3
  [djay]
- Switch to ModifyPortalContent as main permission
  [djay]
- Added a unsubscribe form that allow unsubscribing direcly from the website
  [MrTango]
- Added some test for the unsubscribe views
  [MrTango]
- Reduce code complexity in ENLIssue and fix all pep8 violations
  [MrTango]
- Do the unicode check for handle_startendtag as well
  [jean]



2.6.12 (2013-11-01)
-------------------

- Correct non user fullname show/hide parameter usage: was always showed.
  [MordicusEtCubitus]

- Add French translation.
  [toutpt, MordicusEtCubitus]

- Add @@daily-issue view, in order to send issues with cron or clock-server.
  [tcurvelo]

- Change permission to send daily issue to ManagePortal.
  [tcurvelo]

- Improve responses and tests for daily issues.
  [tcurvelo]

- Adapted to Plone 4.3.
  [ksuess, rohberg]

- Fix exception handling in get_plone_members.
  [derstappenit]

- Fix description for Newsletter Template field in ENLIssue.
  [djowett]

- Add documentation for how to use filter to filter newsletter receivers.
  [MrTango]

- Optimize get_plone_member.
  [MrTango]

- Update Products/EasyNewsletter/content/EasyNewsletter.py 'results' not
  initialized properly in case of an error.
  [zopyx]

- Fix import of getSite for plone3.
  [MrTango]

- Update pt_BR translation.
  [tcurvelo]

- Fix check for already existing subscriber when registering. Hide
  enl_actions viewlet from public audience.
  [petschki]

- Allow registration without chosing a gender.
  [pbauer]

- i18n for default template.
  [davilima6]

- No more global definitions in templates.
  [davilima6]

- Corrections and Anglicization of Default newsletter templates.
  [djowett]


2.6.11 (2012-07-11)
-------------------

- Fix translations
  [derstappenit]

- Move Manage aggregation templates action into object_button aka actions menu
  [derstappenit]


2.6.10 (2012-07-10)
-------------------

- fix the email format, we don't use MIMEMultipart for the plain text part of the email, this fix problems with thunderbird
  [derstappenit]


2.6.9 (2012-07-06)
------------------

- we now use the modification date in Archive and Drafts view
  [derstappenit]

- ENLIssue now only editable if status is not Send
  [derstappenit]

- Newsletter UI cleanup, the archive, drafts and subscriber actions now in a smal viewlet, this reduce the buttons to make it clear
  [derstappenit]

- Issue UI cleanup, the actions for criteria and sub collections are move into object_buttons aka actions menu
  [derstappenit]


2.6.8 (2012-07-03)
------------------

- Improve the default template for content aggregation, we use tabled based layout now
  [derstappenit]

- Improve the output template, we use tabled based layout now
  [derstappenit]

- improve support for @@images view in image urls


2.6.7 (2012.06.11)
------------------

- Fix translations
  [derstappenit]


2.6.6 (2012-06-04)
------------------

- Added Danish translation.
  [malthe]

- Add mailonly filter, to allow elements only in mails but not in public view
  [derstappenit]

- Add support for @@images view in image urls
  [derstappenit]


2.6.5 (2012-05-04)
------------------

- include mo files in MANIFEST, so that they are included in the package
  [derstappenit]

2.6.4 (2012-05-03)
------------------

- add german translations
  [derstappenit]


2.6.3 (2012-04-30)
------------------

- don't override the issue content after first saving
  [derstappenit]

- rename aggregate action and move this action to object_buttons (actions menu)
  [derstappenit]


2.6.2 (2012-04-20)
------------------

- Improved handling utf-8 strings for the import and export for members
  [frapell]

- Added stoneagehtml package for processing the newsletter's html before
  sending it by mail. This add support for css declararions that will be
  written directly into the html tags to improve rendering results in
  email clients.
  [nueces]

- Added Spanish translation.
  [nueces]

- Fix rendering of images in email-clients.
  [wimbou, WouterVH]

- Fix non-ASCII chars in headers. This fixes
  http://plone.org/products/easynewsletter/issues/17 and
  http://plone.org/products/easynewsletter/issues/19
  [regisrouet, WouterVH]

- Fix breaking dexterity by checking on portal_type instead of meta_type.
  [WouterVH]

- When a subscriber is created via addSubscriber, set language same as newsletter.
  (merged from branch-bpi-rouet-2011-9)
  [regisrouet, WouterVH]

- When importing, set subscriber language same as newsletter.
  (merged from branch-bpi-rouet-2011-9)
  [regisrouet, WouterVH]

- Fix unicode characters in title of issue.
  (merged from branch-unicodefix)
  [mircoangelini, WouterVH]

- i18n for the uploaded/downloaded CSV-file.
  [WouterVH]

- Fix Plone3-compatibility when sending MIMEMultipart-messages.
  [WouterVH]

- A regular Editor can now edit and refresh drafts, without needing
  full Manager-permissions.
  [WouterVH]

- Fix unicode decode error when sending newsletter issues with special
  characters in the title.
  [timo]

- Update Brazilian Portuguese translation
  [ericof]

- fix subscriber tempatlae, to remove the the empty p tag if no description is provided
  [derstappenit]

- use radio buttons instead of selection for salutation selection in subscriber template
  [derstappenit]

2.6.1 (2011-11-23)
------------------

- Fix mail rendering in Thunderbird 8.
  [timo]

- Fix German translation for registration notification.
  [timo]

- Use test instead of tests in extras_require to comply with Plone standards.
  [timo]

- Remove test_enl.py tests since it does not test anything that is not covered
  by test_setup.py.
  [timo]


2.6 (2011-10-01)
----------------

- Fix external images url by inserting url directly in html when 'http' is
  encountered. This fixes http://plone.org/products/easynewsletter/issues/15
  [numahel]

- loadContent only when AcquireCriteria is set True.
  Do not override the text when it's False.
  This fixes http://plone.org/products/easynewsletter/issues/4
  [WouterVH]

- Rename "refresh" into "Refresh aggregate body" to make more clear what it
  does. Cfr. http://plone.org/products/easynewsletter/issues/4
  [WouterVH]

- Improve translatable content.
  [wimbou]

- Fix ENLIssue to avoid issue to be sent twice to same recipient.
  [numahell]

- Add Brazilian translation.
  [davilima6]

- Add Dutch translation.
  [WouterVH, wimbou]

- Fix i18n-domain for GS-profiles files.
  [WouterVH]

- Avoid duplicate listing in portal_quickinstaller.
  Fixes http://plone.org/products/easynewsletter/issues/6
  [WouterVH]

- Don't overwrite the metaTypesNotToList-property, but just append our own
  types.
  [WouterVH]


2.5.10a2 (2011-03-11)
---------------------

- Nothing yet.


2.5.10a2 (11/03/2011)
---------------------

- Fix confirm_subscriber and addSubscriber to set salutation from subscribe
  portlet.
  [numahell]

- Fix ENLHTMLParser for unicode URLs.
  [timo]

- Order newsletters and drafts by creation date.
  [timo]

- Set batch_base_url in enl_subscribers_view, this fix the url of batch
  navigation.
  [derstappenit]


2.5.10a1 (15/02/2011)
---------------------

- plone.app.testing test setup added.
  [timo]

- Do not exclude ENL content types from navigation on a content object level.
  Exclude them on content type level in the GS profile.
  [timo]

- Fix UnboundLocalError which comes with the try except statement.
  [derstappenit]

- Fix AttributeError get_all_memberproperties if fmp is available but not
  installed in the quickinstaller.
  [derstappenit]


2.5.9 (15/02/2011)
------------------

- Fix UnboundLocalError: local variable 'o' referenced before assignment, which
  come with the try except to cache image handling errors.
  [derstappenit]


2.5.8 (14/02/2011)
------------------

- Fix optional use of fmp.
  [derstappenit]

- Only add default_template if doesnt exists, this fix error in archetypes_tool
  on update schema.
  [derstappenit]

- Add a BooleanField sendToAllPloneMembers, which can be used to address all
  existing plone members in a newsletter, no need to select all every time new
  user are available.
  [derstappenit]

- Fix url handlink for links and images if url contains empty spaces,
  add z3 resource image support, add images only to html part of the email.
  [derstappenit]

- Cache exception if broken img tags exist that can't be resolved by
  restrictedTraverse, but log the error.
  [derstappenit]


2.5.7 (08/02/2011)
------------------

- Do not encode email addresses when exporting subscribers.
  [timo]

- Make sure the url variable is always set in the handle_starttag method of
  the ENLHTMLParser.
  [timo]

- Fix CSV import with special characters.
  [timo]

- Do not create a persistent file when exporting CSV data, use a temp file
  instead.
  [timo]

- Fix CSV export with special characters.
  [timo]

- Added missing methods for HTML parser in order to preserve HTML references
  and other stuff.
  [dgherman]


2.5.6 (27/01/2011)
------------------

- Create new Sphinx-based documentation.
  [timo]

- Move CSV file format description to the top.
  [timo]

- CSV export added.
  [timo]

- Use TextAreaWidget for the newsletter template body.
  [timo]

- Fix/refactor/rewrite CSV import.
  [timo]

- Fix CSV-Import format description.
  [timo]

- Link to subscriber import added.
  [timo]


2.5.5 (26/01/2011)
------------------

- Remove unneeded dependency to BeautifulSoup.
  [derstappenit]


2.5.4 (11/01/2011)
------------------

- Fix schema of EasyNewsletter and ENLIssues, use copy to create a schema based
  on ATTopicSchema.
  [derstappenit]


2.5.3 (07/01/2011)
------------------

- Fix issue view, now it looks mostly like the html newsletter version in your
  mail client.
  [derstappenit]


2.5.2 (06/01/2011)
------------------

- Add salutation to ENLSubscriber.
  [derstappenit]

- EasyNewsletter and subscriber portlet.
  [derstappenit]

- Make name and salutation optinal in subscriber portlet.
  [derstappenit]

- Remove filter in get_public_body, because we want the look of the public view
  mostly like in the sended mails.
  [derstappenit]

- Optimize issue_send_form to make it more failsave.
  [derstappenit]

- Refacturer the handling of placeholders for salutation and unsubscribelink.
  [derstappenit]

- Reinclude header and footer in mails.
  [derstappenit]

- Fix MultipartMessage-handling, now text and html messages parts have all
  images included.
  [derstappenit]

- Cleanup archetypes schematas of EasyNewsletter and ENLIssue.
  [derstappenit]

- Add many german translations.
  [derstappenit]


2.5.1 (2010/11/30)
------------------

- Added CSV import (to upload_csv.pt, subscribers.py)
  you have to append '@@upload_csv' to your newsletter url to call this page.
  the csv file must look like this (email is required)::

    "fullname","email","organization"
    "John Doe","john.doe@yahoo.com","ACME Corp."
    "","admin@plone.org",""

  [nan]


2.5.0 (2010/11/26)
--------------------

- Final release.


2.5.0b6 (2010/11/24)
--------------------

- Fixed issue default view (``refresh`` documentation did not work).
  [ajung]


2.5.0b5 (2010/11/23)
--------------------

- Fixed error handling in send().
  [ajung]

- Made unsubscribe code more robust.
  [ajung]


2.5.0b4 (2010/11/19)
--------------------

- Compatibility fixes with Plone 3/4.
  [ajung]

- Default template mechanism while creating a new issue did not work.
  [ajung]


2.5.0b3 (2010/11/18)
--------------------

- Subcollections view did not work.
  [ajung]


2.5.0b2 (2010/11/16)
--------------------

- Fixed encoding issue with the member vocabulary.
  [ajung]


2.5.0b1 (2010/11/16)
--------------------

- Added support for Zope utilities providing the ISubscriberSource
  interface to hook in external subscriber sources (e.g. some sub-system
  managing subscriptions to newsletters on their own (instead of relying
  on instances of 'Subscriber' located inside the newsletter folder itself).
  [ajung]

- The 'Subscribers' tab of Issue instance now also includes subscribers
  from an utility providing ISubscriberSource.
  [ajung]

- The Newsletter instance now got an new schemata 'External' and a new
  option to configure an utility providing ISubscriberSource.
  [ajung]

- It is now possible to configure a dedicated MailHost for newsletter
  delivery other than the configured Plone MailHost (see External tab
  of the Newsletter instance). An external delivery service must be
  configured as named utility providing IMailHost.
  [ajung]

- Major refactoring of the send() method of ENLIssue.
  [ajung]

- Added getFiles() API to ENLIssue for auto-generating a listing
  of files attached to the newsletter body upon send time.
  [ajung]

- Personal information like the salutation {% subscriber-fullname %}
  must no longer be located inside the newsletter body but should be
  moved out to the header and footer sections.
  [ajung]

- Replace enl_issue_view with a rendered view of the newsletter without
  header and footer.
  [ajung]

- Added all types to portal_factory configuration.
  [ajung]

- Added @@all_issues_view to Newsletter implementation.
  [ajung]

- Plone 4 compatibility fixes.

- Various cleanup.
  [ajung]


2.0.1 (2010-07-31)
-----------------------

- Bugfix: use the Zope MailHost for conformations mails, instead of sendmail.
  Now you settings in plone sitesetup will respected ;).


2.0 (2010-07-16)
-----------------------

- Integrate the header and footer field into email text.

- Add possibility to define a default header and footer in the Newsletter
  container.

- Add fullname attribute to subscriber.

- Add description and fullname to subscriber portlet.

- Add usefull path description to subscriber portlet and allow also a path
  starting with '/'.

- Add plone members and groups selection to Newsletter and Issue.

- Use inqbus.fastmemberproperties to get all memberproperties fast.
  (inqbus.fastmemberproperties is now required!)

- Add personalization of emails.

- Add PERSOLINE marker to indicate personalize lines, this lines are removed in
  archive view.

- Add TemplateField to the Newsletter container to cutomize the output format
  of the mailing/newsletter.

- Make sending more robust, catch Exceptions and log it, insted of breaking up
  in the middle of sending procedure.

- Move confirmation mail subject and text out into Newsletter settings to make
  it customizeable.

- Add Double Opt-in to subscribe process.


1.0 beta 3 (2009-12-24)
-----------------------

- Removed subscribers and templates from navigation.

- Batch subscribers.


1.0 beta 2 (2009-12-19)
-----------------------

- Added missing non-python files.


1.0 beta 1 (2009-12-19)
-----------------------

- First version for Plone 3.
