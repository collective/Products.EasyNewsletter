EasyNewsletter
==============

.. image:: https://secure.travis-ci.org/collective/Products.EasyNewsletter.png?branch=master
    :target: http://travis-ci.org/collective/Products.EasyNewsletter

.. image:: https://coveralls.io/repos/collective/Products.EasyNewsletter/badge.png?branch=master
    :target: https://coveralls.io/r/collective/Products.EasyNewsletter

EasyNewsletter is a simple but powerful newsletter/mailing product for Plone.


Features
========

* Plain text and HTML newsletters (including images),

* manual written newsletters/mailings,

* automatic Plonish newsletters/mailings: Utilize Plone's Collections to collect content)

* send out daily/weekly/monthly issues automatically,
  based on collections (by cron or clock-server)

* flexible templates to generate newsletter content

* TTW customizable output template to generate HTML newsletters

* personalized emails

* synchronous/ asynchronous sendout (also test emails),

* subscribing/ unsubscribing,

* import/export subscribers via csv

* use Plone Members/Groups as receivers (works also with Membrane),

* external

  * subscriber sources (configured through a Zope utility),
  * delivery services (other than Plone MailHost),

* external subscriber filtering/manipulation with plugins (filter out or add more subscribers)

Requirements
============

* Plone 4.3, 5.0 and 5.1 (tested)
* Archetypes
* ATContentTypes (base profile only)

Optional:

* ``inqbus.plone.fastmemberproperties`` speeds up access of member properties.
  Use ``Products.EasyNewsletter[fmp]`` extra in your buildouts eggs list.
* ``collective.taskqueue`` for asynchronous sendout.
  Use either ``Products.EasyNewsletter[taskqueue]`` or ``Products.EasyNewsletter[taskqueue_redis]`` extra.
  Configure a named task queue ``Products.EasyNewsletter.queue``.
  Read carefully the documentation of ``collective.taskqueue``.
* ``collective.zamqp`` for asynchronous sendout.
  Configure a queue named ``Products.EasyNewsletter.queue``.
* For asynchronous sendout use the one or the other, both together will crash Plone.
  ``collective.taskqueue`` is recommended unless you know why you want to use AMQP.


Installation
============

1. Add ``Products.EasyNewsletter`` to your buildout
2. Run your buildout script
3. Restart zope
4. Install EasyNewsletter via Plone Management Interface
5. Add a "Newsletter Subscriber" portlet and select the EasyNewsletter
   (To this newsletter the subscribers will be added).

Documentation
=============

For more documentation please visit: http://productseasynewsletter.readthedocs.io


Known Issues
============

* If parts of the ENLIssue footer show up in the Plone footer, change the footer portlet view name from ``footer`` to ``@@footer``. This issue was fixed in Plone already, but you have to manually update this in an existing site.


Source Code
===========

Source code is at Github: https://github.com/collective/Products.EasyNewsletter


Bugtracker
==========

Issue tracker is at Github: https://github.com/collective/Products.EasyNewsletter/issues


Authors
=======

* initial release: Kai Dieffenbach
* Maik Derstappen
* Andreas Jung
* Philip Bauer
* Timo Stollenwerk
* Dinu Gherman
* Peter Holzer
* Jens W. Klein
