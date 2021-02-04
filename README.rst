EasyNewsletter
==============

.. image:: https://github.com/collective/Products.EasyNewsletter/workflows/Plone%20package/badge.svg
    :target: https://github.com/collective/Products.EasyNewsletter/actions

.. image:: https://coveralls.io/repos/github/collective/Products.EasyNewsletter/badge.svg?branch=master
    :target: https://coveralls.io/github/collective/Products.EasyNewsletter?branch=master

.. image:: https://img.shields.io/pypi/v/Products.EasyNewsletter.svg
    :target: https://pypi.python.org/pypi/Products.EasyNewsletter/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/status/Products.EasyNewsletter.svg
    :target: https://pypi.python.org/pypi/Products.EasyNewsletter/
    :alt: Egg Status

.. image:: https://img.shields.io/pypi/pyversions/Products.EasyNewsletter.svg
    :target: https://pypi.python.org/pypi/Products.EasyNewsletter/
    :alt: Supported - Python Versions

.. image:: https://img.shields.io/pypi/l/Products.EasyNewsletter.svg
    :target: https://pypi.python.org/pypi/Products.EasyNewsletter/
    :alt: License

EasyNewsletter is a simple but powerful newsletter/mailing add-on for Plone.

Compatibility
-------------

* EasyNewsletter versions >= 5.x are Plone 5.1 and above only, they are free of Archetypes and **support Python 3**.
* EasyNewsletter versions >= 4.x Plone 5.1 only, they are using DX but still have Archetypes dependencies for migration.
* For Plone versions < 5.1, use the 3.x branch and releases of EasyNewsletter!

For Python 2.7 you have to pin down html2text:

    html2text = <2019.8.11


Features
========

* Plain text and HTML newsletters (including images)

* manual written newsletters/mailings

* automatic Plonish newsletters/mailings: Utilize Plone's Collections to collect content)

* send out daily/weekly/monthly issues automatically,
  based on collections (by cron or clock-server)

* flexible templates for Collections, to generate newsletter content

* TTW customizable output template to generate HTML newsletters

* personalized emails

* subscribing/ unsubscribing

* import/export subscribers via CSV

* use Plone Members/Groups as receivers (works also with Membrane)

* external subscriber filtering/manipulation with plugins (filter out or add more subscribers)

* synchronous/ asynchronous send out [currently not reimplemented, if you need this, you have to wait for future versions or fund the work on this feature]

* external

  * subscriber sources (configured through a Zope utility) [currently not reimplemented]
  * delivery services (other than Plone MailHost) [currently not reimplemented]


Requirements
============

* Plone 5.1 (tested)
* Dexterity (Archetypes for migration)


Installation
============

1. Add ``Products.EasyNewsletter`` to your buildout
2. Run your buildout script
3. Restart Plone
4. Install EasyNewsletter via Plone Management Interface
5. Add a Newsletter to the Plone site
6. Add a "Newsletter Subscriber" portlet and select a Newsletter
   (To this newsletter, the subscribers will be added).


Documentation
=============

For more documentation please visit: http://productseasynewsletter.readthedocs.io


Known Issues
============

* If parts of the ENLIssue footer show up in the Plone footer, change the footer portlet view name from ``footer`` to ``@@footer``. This issue was fixed in Plone already, but you have to manually update this in an existing site.


Source Code
===========

Source code is at GitHub: https://github.com/collective/Products.EasyNewsletter


Bug tracker
===========

Issue tracker is at GitHub: https://github.com/collective/Products.EasyNewsletter/issues

ToDo
====

funding welcome ;)

- async task queue for WGSI as an alternative to collective.taskqueue which will not support WGSI
- Integration of Mosaico newsletter editor
- External subscriber sources / delivery services
- content migration AT >> DX


Maintainer
==========

* Maik Derstappen [MrTango] md@derico.de


Contributors
============

* Kai Dieffenbach: initial release
* Andreas Jung
* Dinu Gherman
* Jens W. Klein
* Peter Holzer
* Philip Bauer
* Thomas Massman [tmassmann]
* Timo Stollenwerk
