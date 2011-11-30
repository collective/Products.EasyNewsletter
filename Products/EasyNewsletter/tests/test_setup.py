import unittest2 as unittest

#from zope.component import createObject
#from zope.component import getMultiAdapter
#from zope.component import queryUtility

from Products.EasyNewsletter.testing import \
    EASYNEWSLETTER_INTEGRATION_TESTING

from plone.app.testing import TEST_USER_ID, setRoles
#from plone.app.testing import TEST_USER_NAME, login


class EasyNewsletterSetupTests(unittest.TestCase):

    layer = EASYNEWSLETTER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        self.folder = self.portal['test-folder']

        self.properties = self.portal.portal_properties

    def test_newsletter_factory(self):
        #self.folder.invokeFactory("EasyNewsletter", "newsletter")
        #enl = self._makeOne()
        #enl.invokeFactory('ENLIssue', id='issue')
        #issue = enl['issue']
        #enl.invokeFactory('ENLSubscriber', id='heino')
        #heino = enl['heino']
        pass

    def test_catalog(self):
        indexes = self.portal.portal_catalog.indexes()
        self.assertEqual('email' in indexes, True)
        self.assertEqual('fullname' in indexes, True)
        self.assertEqual('organization' in indexes, True)

    def test_newsletter_subtypes_in_meta_types_not_to_list(self):
        # Hide newsletter subtypes from navigation
        self.failUnless(self.properties.navtree_properties.hasProperty('metaTypesNotToList'))
        self.failUnless('ENLIssue' in self.properties.navtree_properties.metaTypesNotToList)
        self.failUnless('ENLSubscriber' in self.properties.navtree_properties.metaTypesNotToList)
        self.failUnless('ENLTemplate' in self.properties.navtree_properties.metaTypesNotToList)

    def test_newsletter_view(self):
        #self.folder.invokeFactory("EasyNewsletter", "newsletter")
        #view = getMultiAdapter((self.folder.newsletter, self.portal.REQUEST),
        #                       name="view")
        # Put view to acquisition chain
        #view = view.__of__(self.portal)
        # Call view
        #self.failUnless(view())
        pass


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
