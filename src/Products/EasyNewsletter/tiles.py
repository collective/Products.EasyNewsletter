from plone.app.standardtiles.common import ProxyViewletTile


class NewsletterActionsTile(ProxyViewletTile):
    """Newsletter actions tile."""

    manager = "plone.abovecontentbody"
    viewlet = "newsletter-actions"
