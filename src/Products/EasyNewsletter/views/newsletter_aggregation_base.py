# -*- coding: utf-8 -*-

# from Products.EasyNewsletter import _
from Acquisition import aq_inner
from plone.app.contenttypes import _
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.contenttypes.browser.folder import FolderView
from plone.app.contenttypes.interfaces import IFolder
from plone.app.contenttypes.interfaces import IImage
from plone.memoize.view import memoize
from zope.interface import Interface
from zope.interface.declarations import implementer


class INewsletterAggregationBase(Interface):
    """
    """

    def test(self):
        """
        """

    def batch(self):
        """
        """

    def collection_behavior(self):
        """
        """

    def results(self, **kwargs):
        """
        """

    def b_size(self):
        """
        """

    def _album_results(self):
        """Get results to display an album with subalbums.
        """

    def album_images(self):
        """Get all images within this collection.
        """

    def album_folders(self):
        """Get all folders within this collection.
        """

    def tabular_fields(self):
        """Returns a list of all metadata fields from the catalog that were
           selected.
        """

    def no_items_message(self):
        """
        """

@implementer(INewsletterAggregationBase)
class NewsletterAggregationBase(FolderView):

    def test(self):
        """
        """
        return u"ok nur eion string"

    @property
    def collection_behavior(self):
        return ICollection(aq_inner(self.context))

    @property
    def b_size(self):
        return getattr(self, '_b_size', self.collection_behavior.item_count)

    def results(self, **kwargs):
        """Return a content listing based result set with results from the
        collection query.

        :param **kwargs: Any keyword argument, which can be used for catalog
                         queries.
        :type  **kwargs: keyword argument

        :returns: plone.app.contentlisting based result set.
        :rtype: ``plone.app.contentlisting.interfaces.IContentListing`` based
                sequence.
        """
        # Extra filter
        contentFilter = dict(self.request.get('contentFilter', {}))
        contentFilter.update(kwargs.get('contentFilter', {}))
        kwargs.setdefault('custom_query', contentFilter)
        kwargs.setdefault('batch', True)
        kwargs.setdefault('b_size', self.b_size)
        kwargs.setdefault('b_start', self.b_start)

        results = self.collection_behavior.results(**kwargs)
        return results

    def batch(self):
        # collection is already batched.
        return self.results()

    @property
    @memoize
    def _album_results(self):
        """Get results to display an album with subalbums.
        """
        results = self.results()
        images = []
        folders = []
        for it in results:
            # TODO: potentially expensive!
            ob = it.getObject()
            if IImage.providedBy(ob):
                images.append(it)
            elif IFolder.providedBy(ob):
                folders.append(it)
        return {'images': images, 'folders': folders}

    @property
    def album_images(self):
        """Get all images within this collection.
        """
        return self._album_results['images']

    @property
    def album_folders(self):
        """Get all folders within this collection.
        """
        return self._album_results['folders']

    def tabular_fields(self):
        """Returns a list of all metadata fields from the catalog that were
           selected.
        """
        context = aq_inner(self.context)
        wrapped = ICollection(context)
        fields = wrapped.selectedViewFields()
        fields = [field[0] for field in fields]
        return fields

    def no_items_message(self):
        return _(
            'description_no_results_found',
            default=u'No results were found.'
        )
