Python3 and Dexterity upgrade notes
===================================

Plone 5.1 / Python 2.7
----------------------

- Create new DX CT's: Newletter, Newsletter Issue, Newletter Subscriber
- Add DX schema fields mostly like the current AT fields

### Differences

#### Newsletter

##### Schema

    old : new

- senderEmail :  sender_email
- senderName : sender_name
- testEmail : test_email
- contentAggregationSources : content_aggregation_sources
- default_header : default_prologue
- default_footer : default_epilogue
- excludeAllSubscribers : exclude_all_subscribers
- outputTemplate : output_template
- template : aggregation_template

##### Behaviors

- Newsletter: Plone users/groups as recipients
- Newsletter: External subscriber sources
- Newsletter: External delivery services


#### Newsletter Issue

##### Schema

    old : new

-


##### Behaviors

- Newsletter: Plone users/groups as recipients
- Newsletter: Collection as source   [make sure existing Collections have the behavior set with values]


- Implement CT's methods mostly as views/utilities instead of instance methods
- Move aggregation templates into a behavior for Collections, so that every selected collection can have a different aggregation template. This makes the ENLTemplate CT obsolete.
- Upgrade step: Hide AT CT's from Menu
- Upgrade step: Migrate AT content to DX
- Upgrade step: Migrate subscriber portlets to use the new DX objects
- Upgrade step: Remove old AT content


plone 5.2 / Python 2.7/3.7
--------------------------

- Update code for Py3
- Remove AMQP Code
- Deactivate taskqueue code until ZServer supports it under Py3
- Add WSGI Taskqueue > for example RQ
