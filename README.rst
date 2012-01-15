EasyNewsletter
==============

EasyNewsletter is a simple but powerful newsletter/mailing product for Plone.


Features
========

    * Support Text and HTML Newsletter (including images)

    * Support manual written Newsletters/Mailings

    * Plonish (can use Plone's Collections to collect content)

    * Variable templates to generate newsletter content

    * Subscribing / Unsubscribing and can use Plone Members/Groups as receivers (works also with Membrane)

    * support for external subscriber sources (configured through a Zope utility)

    * support for external delivery services (other than Plone MailHost)

    * TTW customizeable output Template to generate nice HTML Newsletter

    * Support personalized mails

    * mass import/export subscribers via csv

    * support external filtering/manipulation (filter out or add more subscribers) plugins

Requirements
============

    * inqbus.plone.fastmemberproperties, speed up access of member properties (optional, you can installed it with Products.EasyNewsletter[all] in your buidlout eggs list)
    * Plone 3.X (tested)
    * Plone 4.X (tested)


Installation
============

    1. Add Products.EasyNewsletter to your buildout

    2. Run your buildout script

    3. Restart zope

    4. Install EasyNewsletter via Plone Management Interface

    5. Add an "Newsletter Subscriber" portlet and select the EasyNewsletter
       (To this newsletter the subscribers will be added).


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

* ``[[SUBSCRIBER_SALUTATION]]``
* ``[[UNSUBSCRIBE]]``


Source Code
===========

In dec 2011 the source code repository was moved from svn-collective to github.

* Old repository: https://svn.plone.org/svn/collective/Products.EasyNewsletter/
* New repository: https://github.com/collective/Products.EasyNewsletter


Bugtracker
==========

* Old: http://plone.org/products/easynewsletter/issues
* New: https://github.com/collective/Products.EasyNewsletter/issues


Authors
=======

* initial release Kai Dieffenbach
* since 2.0 Maik Derstappen
* since 2.5 Andreas Jung
* Philip Bauer
* Timo Stollenwerk
* Dinu Gherman