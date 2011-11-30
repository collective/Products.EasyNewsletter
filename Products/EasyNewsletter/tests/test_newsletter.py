# -*- coding: utf-8 -*-
import unittest2 as unittest

#from zope.component import createObject
#from zope.component import getMultiAdapter
#from zope.component import queryUtility

from Products.EasyNewsletter.testing import \
    EASYNEWSLETTER_INTEGRATION_TESTING

from plone.app.testing import TEST_USER_ID, setRoles
from plone.app.testing import TEST_USER_NAME, login


class EasyNewsletterTests(unittest.TestCase):

    layer = EASYNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']        
        self.portal = self.layer['portal']
        self.folder.invokeFactory("EasyNewsletter", "newsletter")
        self.newsletter = self.folder.newsletter

    def test_send_issue(self):
        self.newsletter.invokeFactory(
            "ENLIssue", 
            id="issue")
        self.newsletter.issue.title=u"This is a very long newsletter issue title with special characters such as äüö. Will this really work?"

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

#raceback (innermost last):
#  Module ZPublisher.Publish, line 127, in publish
#  Module ZPublisher.mapply, line 77, in mapply
#  Module Products.PDBDebugMode.runcall, line 70, in pdb_runcall
#  Module ZPublisher.Publish, line 47, in call_object
#  Module Products.EasyNewsletter.browser.issue, line 23, in send_issue
#  Module Products.EasyNewsletter.content.ENLIssue, line 366, in send
#  Module email.header, line 176, in __init__
#  Module email.header, line 260, in append
#UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 75: ordinal not in range(128)
#*** SyntaxError: invalid syntax (<stdin>, line 1)
#> /usr/lib/python2.6/email/header.py(260)append()
#-> ustr = unicode(s, incodec, errors)
