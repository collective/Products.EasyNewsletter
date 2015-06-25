.. EasyNewsletter documentation master file, created by
   sphinx-quickstart on Thu Jan 27 10:47:48 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to EasyNewsletter's documentation!
==========================================

What is it?
===========

EasyNewsletter is a simple but powerful newsletter/mailing product for Plone.

Features
========

- Support Text and HTML Newsletter (including images)

- Support manual written Newsletters/Mailings

- Plonish (can use Plone's Collections to collect content)

- Variable templates to generate newsletter content

- Subscribing / Unsubscribing and can use Plone Members/Groups as receivers (works also with Membrane)

- support for external subscriber sources (configured through a Zope utility)

- support for external delivery services (other than Plone MailHost)

- TTW customizeable output Template to generate nice HTML Newsletter

- Support personalized mails

- Mass import/export subscribers via csv

- Support external filtering/manipulation (filter out or add more subscribers) plugins

- Support for creating and sending a daily issue

- Support for decoupled sendout

Requirements
============

- [inqbus.plone.fastmemberproperties] speed up access of member properties
  (optional, you can installed it with Products.EasyNewsletter[all] in your
  buidlout eggs list)

 Plone 3.X (tested) or 4.X (tested)


Installation
============

1. Add Products.EasyNewsletter to your buildout

2. Run your buildout script

3. Restart Zope

4. Install EasyNewsletter via Plone Management Interface

5. Add an "Newsletter Subscriber" portlet and select the EasyNewsletter
   (To this newsletter the subscribers will be added).

Usage
=====

General
-------
You can use EasyNewsletter to manually create mailings/newsletters
or you can use the collection criteria to collect content.

EasyNewsletter is heavily based on Plone's Collections. In fact, the
Newsletter as well as the Issues are actually specialized Collections.

Hence you can use familiar criteria to decide which content should be part of
a newsletter.

It's a feature of Collections that subtopics are able to inherit criteria
from its parent, so all Issue instances are able to inherit criteria from the
outer Newsletter instance.

Plone's default feature of subtopics is used to create sections within the
newsletter issue. For example one can create two sections - news and events - by
creating subtopics which collect just this kind of content objects.

Once the content is generated one can edit the text as usual in Plone.

You can create your own templates to structure the selected content. Please refer
to the provided "default" template to see how it works.

Step by step
------------

1. Add a EasyNewsletter instance, fill in the form and save it.

2. If you want to write a simple manual mailing, you can add an Issue and fill it out with your text.

3. Or if you want to use collections to collect you content first, then you can add an Issue,
   go to Criteria tab and add the criteria, which shall be applied to *all* of
   your Newsletters, e.g. "Items Type".

4. You can create more than one subcollection to build categories like news, events and pictures in your newsletter.
   Just add some collections to the newsletter itself and define your criteria for all of them.
   The issues will combine them into different part in your content area.

5. Go to the view tab and call ``Aggregate body content`` from the action menu.

6. You can also add subcollections and define criteria on Issue level.

7. Go to Send tab and push ``Test Newsletter``.

8. If your Newsletter/Mailing is finished, you can activate the send button by clicking on ``Enable send button``.
   Then you can click on ``Send newsletter`` to send the Newsletter to all subscribers or selected groups and users.

Issue workflow information
--------------------------

There are now four workflow states for an issue, which are draft, sending, sent and master.
If an issue is created, it's initial state is draft.

Only issues with state draft can be send.

If a sendout is started, the state will move to sending.

After an issue is sent, it's state is sent and it will appear in the newsletter archive.

In addition a master can be made out of an issue with the state draft or sent using the actions menu.
The master acts as a blueprint, which can be reedited and copied as a new draft.

Images in HTML mails
--------------------

- All images with relative urls in ``src`` attribute, like the ones added by TinyMCE, are included and attached to the mail.
- All images with absolute urls in ``src`` attribute are not attached but included in HTML with the original ``src`` url.

Elements for mails only
-----------------------

If you want some elements, let's say a logo only in mails but not in the public view, you can put it inside a div tag with a class "mailonly". All div elements with class "mailonly" are filtered out in the public view.

Asyncronous sendout
-------------------

Products.EasyNewsletter supports asyncronous sendout using collective.zamqp. Look at the self contained buildout or https://pypi.python.org/pypi/collective.zamqp and add Products.EasyNewsletter[zamqp] to your eggs section. If you have configured your buildout according accordingly, Products.EasyNewsletter will automatically delegate the sendout to your worker instance.

Sending a daily issue automatically
-----------------------------------
EasyNewsletter can create and send daily issues, using the default template and
default criteria. Beside those, you just need to configure your crontab (or
clock server) to send a `POST` on `@@daily-issue` view.
Eg::
    #Sends a newsletter, from Mon to Fri, at 0:00AM
    0 0 * * 1-5 curl -X POST http://user:passwd@example.org/mynewsletter/@@daily-issue

`@@daily-issue` returns a HTTP status code indicating what just happened (you
can also test it with a GET, instead). In the table below, you can check the
responses codes.

===================  ============  =====  ============
@@daily-issue responses
------------------------------------------------------
Method/Precondition  Not yet sent  Empty  Already Sent
===================  ============  =====  ============
GET                     100         204       200
POST                    200 [*]_    204       409
===================  ============  =====  ============

.. [*] It sends the issue first.


Filtering Users, Groups and Receivers
-------------------------------------

EasyNewsletter provide a flexible way to filter the Plone members, Plone groups and the recivers list. You can provide smal funtion in your add-on and register it as IReceiversMemberFilter, IReceiversGroupFilter or IReceiversPostSendingFilter. The filter get the list and can filter out some entries or even add some entries.

IReceiversMemberFilter filters
""""""""""""""""""""""""""""""
``Interface: Products.EasyNewsletter.interfaces.IReceiversMemberFilter``

The IReceiversMemberFilter filters can be used to filter the list of Plone members which a user can select in newsletters and issues.

::

   class ReceiversMemberFilterNoPloneMember(object):
       """ filters all members out of newsletter receivers selection list,
           which are default plone members. This is usefull if you whant
           only membrane members but not the default plone user as receivers.
           receivers: [(id, {'email': 'info@example.com',...})]
       """

       def __init__(self, context):
           self.context = context

       def filter(self, receivers):
           portal = getSite()
           query = {}
           query['portal_type'] = ['Contact',]
           contacts = portal.membrane_tool.search(query)
           whitelist = [contact.getUserId for contact in contacts]
           receivers = [receiver for receiver in receivers
                   if receiver[0] in whitelist]
           return receivers

**This filter should be registered as follow:**

::

    <subscriber zcml:condition="installed my.package"
        for="Products.EasyNewsletter.interfaces.IEasyNewsletter"
        factory="my.package.newsletter.ReceiversMemberFilterNoPloneMember"
        provides="Products.EasyNewsletter.interfaces.IReceiversMemberFilter" />


IReceiversGroupFilter filters
"""""""""""""""""""""""""""""
``Interface: Products.EasyNewsletter.interfaces.IReceiversGroupFilter``

The IReceiversGroupFilter filters can be used to filter the list of Plone groups which a user can select in newsletters and issues.

::

   class ReceiversGroupFilterInactiveOrganizations(object):
       """ Filter all inactive organizations, out of the group selection list.
           receivers: [(id, {'email': 'info@example.com',...})]
       """

       def __init__(self, context):
           self.context = context

       def filter(self, receivers):
           portal = getSite()
           query = {}
           query['portal_type'] = ['Organization']
           query['review_state'] = ['inactive', 'internal', 'pending', 'former_member']
           inactive_groups = portal.membrane_tool.search(query)
           blacklist = [black.getGroupId for black in inactive_groups]
           receivers = [receiver for receiver in receivers
                   if receiver[0] not in blacklist]
           return receivers

**This filter should be registered as follow:**

::

    <subscriber zcml:condition="installed my.package"
        for="Products.EasyNewsletter.interfaces.IEasyNewsletter"
        factory="my.package.newsletter.ReceiversGroupFilterInactiveOrganizations"
        provides="Products.EasyNewsletter.interfaces.IReceiversGroupFilter" />


IReceiversPostSendingFilter filters
"""""""""""""""""""""""""""""""""""
``Interface: Products.EasyNewsletter.interfaces.IReceiversMemberFilter``

The IReceiversPostSendingFilter can be used to filter the list of reveivers before sending emails to all receivers.

::

   class ReceiversPostSendingFilterNoNewsletter(object):
       """ Filter all contacts that has not set the receive_newsletter
       flag, out of receivers email list. But only if the Newsletter provide
       IReceiversMemberFilterNoNewsletter.
       receivers: [{'email': 'info@example.com',...}]
       """

       def __init__(self, context):
           self.context = context

       def filter(self, receivers):
           newsletter_object = self.context
           if IReceiversMemberFilterNoNewsletter.providedBy(newsletter_object):
               portal = getSite()
               query = {}
               query['portal_type'] = ['Contact']
               query['getReceive_newsletter'] = False
               no_enl_contacts = portal.membrane_tool.search(query)
               blacklist = [black.getUserId for black in no_enl_contacts]
               receivers = [receiver for receiver in receivers
                       if receiver['email'] not in blacklist]
           return receivers

**This filter should be registered as follow:**

::

    <subscriber zcml:condition="installed my.package"
        for="Products.EasyNewsletter.interfaces.IEasyNewsletter"
        factory="my.package.newsletter.ReceiversPostSendingFilterNoNewsletter"
        provides="Products.EasyNewsletter.interfaces.IReceiversPostSendingFilter" />


Configuring external subscriber sources
---------------------------------------

An external subscriber sources provides (additional) subscriber to a newsletter instance.

You configure an external subscriber source as a Zope 3 utility providing ISubscriberSource
(here's an example where subscriptions are managed externally through MongoDB)::


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
            for user in myinfo.accounts.find({'data.newsletters': uid, 'state': 'active'}):
                subscribers.append(dict(email=user['email'], fullname=user['username']))
            return subscribers


The utility must be registered using ZCML::

    <utility zcml:condition="installed Products.EasyNewsletter"
        name="MyInfo subscribers"
        factory=".newsletter.NewsletterSource"
        />

Inside the ``Edit`` view of the instance under the ``External`` tab you should find
``MyInfo subscribers`` under the option ``External subscriber source``.


Allowed placeholders
====================

The following placeholder can be used in the header, body and footer of Issues:

* ``[[SUBSCRIBER_SALUTATION]]``
* ``[[UNSUBSCRIBE]]``


Documentation
=============

For more documentation please visit: http://packages.python.org/Products.EasyNewsletter/


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

* initial release: Kai Dieffenbach
* Maik Derstappen
* Andreas Jung
* Philip Bauer
* Timo Stollenwerk
* Dinu Gherman
* Jens Klein
* Peter Holzer


Contents:

.. toctree::
   :maxdepth: 2


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

