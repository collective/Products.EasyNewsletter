Python3 and Dexterity upgrade notes
===================================

Plone 5.1 / Python 2.7
----------------------

- Create new DX CT's
- Add DX schema fields mostly like the current AT fields
- Implement CT's methods mostly as views/utilities instead of instance methods
- Move aggregation templates into a behavior for Collections, so that every selected collection can have a different aggregation template. This makes the ENLTemplate CT obsolet.
- Upgrade step: Hide AT CT's from Menu
- Upgrade step: Migrate AT content to DX
- Upgrade step: Remove old AT content


plone 5.2 / Python 2.7/3.7
--------------------------

- Update code for Py3
- Remove AMQP Code
- Deactivate taskqueue code until ZServer supports it under Py3
- Add WSGI Taskqueue > for example RQ
