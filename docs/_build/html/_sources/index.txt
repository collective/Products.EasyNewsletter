==========================================
Welcome to EasyNewsletter's documentation!
==========================================

What is it?
===========

EasyNewsletter is a simple newsletter product for Plone.

Features
========

- Plonish (uses Plone's Collections to collect content)

- Subscribing / Unsubscribing

- Variable templates to generate a newsletter

Installation
============

1. Add Products.EasyNewsletter to your buildout

2. Run your buildout script

3. Restart zope

4. Install EasyNewsletter via Plone Management Interface

5. Add an "Newsletter Subscriber" portlet and enter the path to the
   EasyNewsletter object, e.g.: /portal/newsletter (To this newsletter the
   subscribers will be added).

Usage
=====

General
-------
EasyNewsletter is heavily based on Plone's Collections. In fact, the
Newsletter as well as the Issues are actually specialized Collections.

Hence you can use familiar criteria to decide which content should be part of
a newsletter.

It's a feature of Collections that sub topics are able to inherit criteria
from its parent, so all Issue instances are able to inherit criteria from the
outer Newsletter instance.

Plone's default feature of sub topics is used to create sections within the
newsletter issue. For example one can create to sections: news and events by
creating sub topics which collect just this kind of content objects.

Once the content is generated one could edit the text as ususal in Plone.

You can create own templates to structure the selected content. Please refer
to the provided "default"-template to see how it works.

Step by step
------------

1. Add a EasyNewsletter instance, fill in the form and save it.

2. Go to criteria tab and add the criteria, which shall be applied to *all* of 
   your Newsletters, e.g. "Items Type".

3. Add a Newsletter instance, fill in the form and save it.

4. Go to criteria tab and add the criteria, which shall be applied to *this* 
   Newsletter, e.g. "Creation Date",

5. Go to the view tab and press refresh (see Plone's document actions at the 
   bottom of the page)

6. Go to send tab and push "Test Newsletter".
