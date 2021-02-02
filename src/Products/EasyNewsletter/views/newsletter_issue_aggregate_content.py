# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from copy import copy
from plone import api
from plone.app.textfield import RichTextValue
from Products.CMFPlone.utils import safe_unicode
from Products.EasyNewsletter import _
from Products.EasyNewsletter.config import AGG_SOURCES_INFOS
from Products.Five.browser import BrowserView
# from transaction import commit
from zope.annotation import IAnnotations


class NewsletterIssueAggregateContent(BrowserView):
    def __call__(self):
        text = self.render_aggregation_sources()
        self.context.text = RichTextValue(
            raw=text, mimeType="text/html", outputMimeType="text/html",
        )
        api.portal.show_message(
            message=_("Newsletter content successfully aggregated."),
            request=self.request,
            type="info",
        )
        self.request.response.setHeader('Pragma', 'no-cache')
        self.request.response.setHeader('Cache-Control', 'no-cache')
        return self.request.response.redirect(self.context.absolute_url(), status=301)

    def render_aggregation_sources(self):
        """
        """
        results_text = u""
        portal = api.portal.get()
        sources = self.context.content_aggregation_sources

        # clear AGG_SOURCES_INFOS in annotations:
        annotations = IAnnotations(aq_inner(self.context))
        if AGG_SOURCES_INFOS in annotations:
            del annotations[AGG_SOURCES_INFOS]

        for source in sources:
            source_obj = source.to_object
            sresults = source_obj.queryCatalog()
            if not sresults:
                continue
            result_info = {
                "id": source_obj.id,
                "title": source_obj.Title(),
                "description": source_obj.Description(),
                "uid": source_obj.UID(),
                "portal_type": sresults[0].portal_type,
                "brains": sresults,
                "brains_count": len(sresults),
            }

            template_id = source_obj.aggregation_template
            if not template_id:
                template_id = "aggregation_generic_listing"
            template_obj = portal.restrictedTraverse(str(template_id))
            results_text += template_obj(result_info=result_info)
            self.store_source_info_in_annotation(result_info)
        return safe_unicode(results_text)

    def store_source_info_in_annotation(self, source_info):
        """
        """
        # import pdb; pdb.set_trace()
        annotations = IAnnotations(aq_inner(self.context))
        if AGG_SOURCES_INFOS not in annotations:
            annotations[AGG_SOURCES_INFOS] = []
        sinfo = copy(source_info)
        # remove brains, we can't pickle them
        del sinfo['brains']
        annotations[AGG_SOURCES_INFOS].append(sinfo)
