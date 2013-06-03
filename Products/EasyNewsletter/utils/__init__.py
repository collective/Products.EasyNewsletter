try:
    from zope.site.hooks import getSite
except ImportError:
    try:
        from zope.app.component.hooks import getSite
    except ImportError:
        from zope.component.hooks import getSite
from Products.CMFPlone.utils import safe_unicode


def safe_portal_encoding(string):
    portal = getSite()
    props = portal.portal_properties.site_properties
    charset = props.getProperty("default_charset")
    return safe_unicode(string).encode(charset)
