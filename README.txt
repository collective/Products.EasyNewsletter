EasyNewsletter
==============

EasyNewsletter is a simple but powerful newsletter/mailing product for Plone.


Features
========

    * Plonish (can use Plone's Collections to collect content)

    * Support Text and HTML Newsletter (including images)

    * Subscribing / Unsubscribing and can use Plone Members/Groups as receivers (works also with Membrane)

    * support for external subscriber sources (configured through a Zope utility)

    * support for external delivery services (other than Plone MailHost)

    * Variable templates to generate newsletter content

    * TTW customizeable output Template to generate nice HTML Newsletter

    * Support personalized mails

    * mass import subscribers with csv upload

Requirements
============

    * inqbus.plone.fastmemberproperties, speed up access of member properties (should automaticly installed)
    * Plone 3.X (tested)
    * Plone 4.X (slightly tested)


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

Configuring external subscriber sources
=======================================

An external subscriber sources provides (additional) subscriber to a newsletter instance.

You configure an external subscriber source as Zope 3 utility providing ISubscriberSource
(here an example where subscriptions are managed external through MongoDB)::


    class NewsletterSource(object):

        implements(ISubscriberSource)

        def getSubscribers(self, newsletter):
            """ return all subscribers for the given newsletter
                from the MyInfo user database. Newsletter subscriptions
                are referenced inside MyInfo through UIDs.
            """

            uid = newsletter.UID()

            # find MyInfo subscribers
            myinfo = getUtility(IMyInfo)
            subscribers = list()
            for user in myinfo.accounts.find({'data.newsletters' : uid, 'state' : 'active'}):
                subscribers.append(dict(email=user['email'],
                                        fullname=user['username']))
            return subscribers


The utility must be registered using ZCML::

    <utility zcml:condition="installed Products.EasyNewsletter"
        name="MyInfo subscribers"
        factory=".newsletter.NewsletterSource" />

Inside the ``Edit`` view of the instance under the ``External`` tab you should find
``MyInfo subscribers`` under the option ``External subscriber source``.

Allowed placeholders
====================

The following placeholder can be used in the header, body and footer of issues:

* ``{% subscriber-fullname %}``
* ``{% unsubscribe %}``


Source Code
===========

The source code is within the collective: https://svn.plone.org/svn/collective/Products.EasyNewsletter/


Bugtracker
==========

* http://plone.org/products/easynewsletter/issues

Autors
======

* Kai Dieffenbach (V 1.X)
* Maik Derstappen (V 2.0)
* Andreas Jung (V 2.5)

Changes
=======

dev/trunk (2010/11/30)
--------------------
 * added CSV import (to upload_csv.pt, subscribers.py)
   you have to append '@@upload_csv' to your newsletter url to call this page.
   the csv file must look like this (email is required):
    "fullname","email","organization"
    "John Doe","john.doe@yahoo.com","ACME Corp."
    "","admin@plone.org",""
   [nan]

2.5.0 (2010/11/26)
--------------------

 * final release

2.5.0b6 (2010/11/24)
--------------------

 * fixed issue default view (``refresh`` documentation did not work)
   [ajung]


2.5.0b5 (2010/11/23)
--------------------
 * fixed error handling in send()
   [ajung]

 * made unsubscribe code more robust
   [ajung]

2.5.0b4 (2010/11/19)
--------------------
 * compatibility fixes with Plone 3/4
   [ajung]

 * default template mechanism while creating a new issue did not work
   [ajung]

2.5.0b3 (2010/11/18)
--------------------
 * subcollections view did not work
   [ajung]

2.5.0b2 (2010/11/16)
--------------------
 * fixed encoding issue with the member vocabulary
   [ajung]

2.5.0b1 (2010/11/16)
--------------------

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

 * added @@all_issues_view to Newsletter implementation
   [ajung]

 * Plone 4 compatibility fixes

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
