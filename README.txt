EasyNewsletter
============== 

A newsletter for Plone.

Features
========

- Plone-ish (uses Plone's Collections to collect content)

- Subscribing / Unsubscribing

- Variable templates to structure content

Documentation 
=============

For more documentation please visit: http://packages.python.org/Products.EasyNewsletter/

Source Code 
===========

The source code is within the collective: https://svn.plone.org/svn/collective/Products.EasyNewsletter/

Changes
=======

1.1.1 unreleased
--------------
* Removed deprecated IndexItererator from NewsletterTemplateWidget.pt
* Fixed bug in HTML parser, images with relative link are parsed properly
* Fixed bug in sending mechanism 

1.1 (branch for Plone 4, 2010-02-19)
------------------------------------
* Compatible with Plone 4
* Utility for listing subscribers
* One-state private subcriber workflow, anonymous users can subscribe
* Changed permission for sending newsletter, from portal manager to editor
* When subscribing to a newsletter, a confirmation mail is sent.
* Updated all translation files
* Added Dutch translations
* Currently only works with Products.TemplateFields from subversion (trunk).

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
