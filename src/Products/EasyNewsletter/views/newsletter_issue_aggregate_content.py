# -*- coding: utf-8 -*-
from plone import api
from plone.app.textfield import RichTextValue
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView


class NewsletterIssueAggregateContent(BrowserView):
    def __call__(self):
        text = self.render_aggregation_sources()
        self.context.text = RichTextValue(
            raw=text,
            mimeType="text/html",
            outputMimeType="text/html",
        )
        return self.request.response.redirect(self.context.absolute_url(), status=301)

    def render_aggregation_sources(self):
        """
        """
        results_text = u""
        portal = api.portal.get()
        sources = self.context.content_aggregation_sources
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
            template_obj = portal.restrictedTraverse(str(template_id))
            results_text += template_obj(result_info=result_info)
        return safe_unicode(results_text)
