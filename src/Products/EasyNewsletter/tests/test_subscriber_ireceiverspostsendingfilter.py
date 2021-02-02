# -*- coding: utf-8 -*-

from datetime import datetime
from plone import api
from plone.app.testing import setRoles, TEST_USER_ID
from Products.EasyNewsletter.content.newsletter_issue import ISendStatus
from Products.EasyNewsletter.subscriber import FilterAlreadySentReceivers
from Products.EasyNewsletter.testing import PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING

import unittest


class FilterAlreadySentReceiversTests(unittest.TestCase):
    """"""
    layer = PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.newsletter = api.content.create(
            container=self.portal, type='Newsletter', id='newsletter',
        )
        self.issue = api.content.create(
            container=self.newsletter, type='Newsletter Issue', id='issue',
        )

    def test_filter(self):
        """Validate already sent emails are filtered out."""

        receivers = [
            {
                'email': 'john@example.com',
                'fullname': 'John Doe',
                'firstname': 'John',
                'lastname': 'Doe',
                'salutation': 'Dear Mr.',
            },
            {
                'email': 'mary@example.com',
                'fullname': 'Mary Doe',
                'firstname': 'Mary',
                'lastname': 'Doe',
                'salutation': 'Dear Mrs.',
            },
        ]

        successful_receivers = [{
            'email': 'john@example.com',
            'fullname': 'John Doe',
            'firstname': 'John',
            'lastname': 'Doe',
            'salutation': 'Dear Mr.',
            'status': {
                'successful': True,
                'error': None,
                'datetime': datetime.now(),
            },
        }]

        already_sent = FilterAlreadySentReceivers(self.issue)
        final_receivers = already_sent.filter(receivers)
        self.assertEquals(len(final_receivers), 2)

        status_adapter = ISendStatus(self.issue)
        status_adapter.add_records(successful_receivers)

        final_receivers = already_sent.filter(receivers)
        self.assertEquals(len(final_receivers), 1)
