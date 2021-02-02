# -*- coding: utf-8 -*-

from datetime import datetime
from plone import api
from plone.app.testing import setRoles, TEST_USER_ID
from Products.EasyNewsletter.content.newsletter_issue import ISendStatus
from Products.EasyNewsletter.testing import PRODUCTS_EASYNEWSLETTER_INTEGRATION_TESTING

import unittest


class SendStatusTests(unittest.TestCase):
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

    @property
    def receivers(self):
        return [
            {
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
            },
            {
                'email': 'Joe@example.com',
                'fullname': 'Joe Doe',
                'firstname': 'Joe',
                'lastname': 'Doe',
                'salutation': 'Dear Mr.',
                'status': {
                    'successful': False,
                    'error': 'Some error message',
                    'datetime': datetime.now(),
                },
            },
            {
                'email': 'mary@example.com',
                'fullname': 'Mary Doe',
                'firstname': 'Mary',
                'lastname': 'Doe',
                'salutation': 'Dear Mrs.',
            },
        ]

    def test_add_records(self):
        """Validate the 'add_records' method."""
        status_adapter = ISendStatus(self.issue)
        status_adapter.add_records(self.receivers)
        self.assertEquals(len(status_adapter.get_keys()), 3)

        # Adding the same records will not give more items.
        status_adapter.add_records(self.receivers)
        self.assertEquals(len(status_adapter.get_keys()), 3)

        # Adding a new record will reurn more items.
        status_adapter.add_records([{'email': 'info@example.com'}])
        self.assertEquals(len(status_adapter.get_keys()), 4)

    def test_get_records(self):
        """Validate the 'get_records' method."""
        status_adapter = ISendStatus(self.issue)
        status_adapter.add_records(self.receivers)
        self.assertEquals(len(status_adapter.get_records()), 3)
        self.assertEquals(len(status_adapter.get_records(successful=True)), 1)
        self.assertEquals(len(status_adapter.get_records(successful=False)), 1)

    def test_get_keys(self):
        """Validate the 'get_keys' method."""
        status_adapter = ISendStatus(self.issue)
        status_adapter.add_records(self.receivers)
        self.assertEquals(len(status_adapter.get_keys()), 3)
        self.assertEquals(len(status_adapter.get_keys(successful=True)), 1)
        self.assertEquals(len(status_adapter.get_keys(successful=False)), 1)

    def test_reset_statistics_making_master(self):
        """Validate statistics are reset when issue is made as master."""
        status_adapter = ISendStatus(self.issue)
        status_adapter.add_records(self.receivers)
        self.assertEquals(len(status_adapter.get_keys()), 3)
        request = self.issue.REQUEST
        request['enlwf_guard'] = True
        api.content.transition(obj=self.issue, transition='make_master')
        self.assertEquals(len(status_adapter.get_keys()), 0)
        request['enlwf_guard'] = False
