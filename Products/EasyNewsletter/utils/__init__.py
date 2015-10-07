# -*- coding: utf-8 -*-
try:
    from zope.site.hooks import getSite
except ImportError:
    try:
        from zope.app.component.hooks import getSite
    except ImportError:
        from zope.component.hooks import getSite
from Products.CMFPlone.utils import safe_unicode

try:
    from plone.app.upgrade import v50
    from plone.protect.utils import addTokenToUrl
except ImportError:
    def addTokenToUrl(url):
        return url


def safe_portal_encoding(string):
    portal = getSite()
    props = portal.portal_properties.site_properties
    charset = props.getProperty("default_charset", 'utf8')
    return safe_unicode(string).encode(charset)
