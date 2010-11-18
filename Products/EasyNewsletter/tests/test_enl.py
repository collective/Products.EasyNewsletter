
import os
import base
import unittest

from Products.PloneTestCase.PloneTestCase import PloneTestCase

class EasyNewsletterTests(PloneTestCase):

    def afterSetUp(self):
        self.portal.portal_membership.addMember('admin', 'secret', ('Manager',), None)
             
    def testInstallation(self):
        self.login('admin')
        self.portal.invokeFactory('EasyNewsletter', id='newsletter')
        enl = self.portal['newsletter']
        enl.invokeFactory('ENLIssue', id='issue')
        issue = enl['issue']
        enl.invokeFactory('ENLSubscriber', id='heino')
        heino = enl['heino']

    def testCatalog(self):
        self.login('admin')
        indexes = self.portal.portal_catalog.indexes()
        self.assertEqual('email' in indexes, True)
        self.assertEqual('fullname' in indexes, True)
        self.assertEqual('organization' in indexes, True)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EasyNewsletterTests))
    return suite

