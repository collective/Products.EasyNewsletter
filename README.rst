EasyNewsletter
==============

EasyNewsletter is a simple but powerful newsletter/mailing product for Plone.


Features
========

* Support Text and HTML Newsletter (including images)

* Support manual written Newsletters/Mailings

* Plonish (can use Plone's Collections to collect content)

* Variable templates to generate newsletter content

* Subscribing / Unsubscribing and can use Plone Members/Groups as receivers
(works also with Membrane)

* support for external subscriber sources (configured through a Zope utility)

* support for external delivery services (other than Plone MailHost)

* TTW customizeable output Template to generate nice HTML Newsletter

* Support personalized mails

* Support for sending daily issues automatically, based on collections
  (by cron or clock-server)

* mass import/export subscribers via csv

* support external filtering/manipulation (filter out or add more subscribers) plugins

Requirements
============

* [inqbus.plone.fastmemberproperties] speed up access of member properties
  (optional, you can installed it with Products.EasyNewsletter[all] in your
  buidlout eggs list)

* Plone 3.X (tested) or 4.X (tested)

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
