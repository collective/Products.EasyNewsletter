EasyNewsletter
==============

EasyNewsletter is a simple but powerful newsletter/mailing product for Plone.


Features
========

    * Plonish (can use Plone's Collections to collect content)

    * Support Text and HTML Newsletter (including images)

    * Subscribing / Unsubscribing and can use Plone Members/Groups as receivers (works also with Membrane)

    * Variable templates to generate newsletter content

    * TTW customizeable output Template to generate nice HTML Newsletter

    * Support personalized mails


Requirements
============

    * inqbus.plone.fastmemberproperties, speed up access of member properties (should automaticly installed)


Installation
============

    1. Add Products.EasyNewsletter to your buildout

    2. Run your buildout script

    3. Restart zope

    4. Install EasyNewsletter via Plone Management Interface

    5. Add an "Newsletter Subscriber" portlet and enter the path to the
    EasyNewsletter object, e.g.: /portal/newsletter (To this newsletter the
    subscribers will be added).


Documentation 
=============

For more documentation please visit: http://packages.python.org/Products.EasyNewsletter/


Source Code 
===========

The source code is within the collective: https://svn.plone.org/svn/collective/Products.EasyNewsletter/

Autors
======

* Kai Dieffenbach (V 1.X)
* Maik Derstappen (V 2.0)
* Andreas Jung (V 2.1)

Changes
=======

2.1.0 (unreleased)
------------------

 * added support for Zope utilities providing the ISubscriberSource
   interface to hook in external subscriber sources (e.g. some sub-system
   managing subscriptions to newsletters on their own (instead of relying
   on instances of 'Subscriber' located inside the newsletter folder itself)
   [ajung]

 * the 'Subscribers' tab of Issue instance now also includes subscribers
   from an utility providing ISubscriberSource 
   [ajung]

 * the Newsletter instance now got an new schemata 'External' and a new
   option to configure an utility providing ISubscriberSource
   [ajung]

 * it is now possible to configure a dedicated MailHost for newsletter
   delivery other than the configured Plone MailHost (see External tab
   of the Newsletter instance). An external delivery service must be   
   configured as named utility providing IMailHost.
   [ajung]
   
 * major refactoring of the send() method of ENLIssue
   [ajung]    
 
 * added getFiles() API to ENLIssue for auto-generating a listing 
   of files attached to the newsletter body upon send time
   [ajung]    

 * personal information like the salutation {% subscriber-fullname %}
   must no longer be located inside the newsletter body but should be
   moved out to the header and footer sections.
   [ajung]    

 * replace enl_issue_view with a rendered view of the newsletter without
   header and footer
   [ajung]    

 * added all types to portal_factory configuration
   [ajung]

 * various cleanup
   [ajung]


2.0.1 (2010-07-31)
-----------------------

 * bugfix: use the Zope MailHost for conformations mails, instead of sendmail.
   Now you settings in plone sitesetup will respected ;).

Changes
=======

2.0 (2010-07-16)
-----------------------

 * integrate the header and footer field into email text

 * add possibility to define a default header and footer in the Newsletter container 

 * add fullname attribute to subscriber

 * add description and fullname to subscriber portlet
 
 * add usefull path description to subscriber portlet and allow also a path starting with '/'

 * add plone members and groups selection to Newsletter and Issue

 * use inqbus.fastmemberproperties to get all memberproperties fast (inqbus.fastmemberproperties is now required!)

 * add personalization of emails

 * add PERSOLINE marker to indicate personalize lines, this lines are removed in archive view

 * add TemplateField to the Newsletter container to cutomize the output format of the mailing/newsletter

 * make sending more robust, catch Exceptions and log it, insted of breaking up in the middle of sending procedure

 * move confirmation mail subject and text out into Newsletter settings to make it customizeable

 * add Double Opt-in to subscribe process


1.0 beta 3 (2009-12-24)
-----------------------
* Removed subscribers and templates from navigation

* Batch subscribers

1.0 beta 2 (2009-12-19)
-----------------------

* Added missing non-python files

1.0 beta 1 (2009-12-19)
-----------------------

* First version for Plone 3
