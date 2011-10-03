import HTMLParser
import urlparse
import urllib

from Products.CMFCore.utils import getToolByName

import logging
logger = logging.getLogger("Products.EasyNewsletter.HTMLParser")


class ENLHTMLParser(HTMLParser.HTMLParser):
    """A simple parser which exchange relative URLs with absolute ones"""

    def __init__(self, context):

        self.context = context
        self.html = ""
        self.image_urls = []
        self.image_number = 0
        plone_utils = getToolByName(self.context, 'plone_utils')
        self.encoding = plone_utils.getSiteEncoding()
        # portal_url could also be taken from a newsletter parameter for people having public/private url
        self.portal_url = getToolByName(context, "portal_url")()

        HTMLParser.HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        """
        """
        self.html += "<%s" % tag


        for attr in attrs:
            if attr[0] == "href":
                url_tuple = urlparse.urlsplit(attr[1])
                if url_tuple.scheme != '':
                    url = attr[1]
                elif url_tuple.path.startswith('/'):
                    url = '%s%s' % (self.portal_url, attr[1])
                elif url_tuple.path.startswith('resolveuid/'):
                    # consider resolveuid url as absolute
                    # on sept 2011, TinyMCE create link ref as "resolveuid/..." 
                    url = '%s/%s' % (self.portal_url, attr[1])
                elif 'resolveuid/' in url_tuple.path:
                    # on sept 2011, by default, TinyMCE convert user inserted absolute link to relative ones, ex; ../../../my_abs_url
                    # this could help if this hasn't been applied : http://stackoverflow.com/questions/5196205/disable-tinymce-url-conversions
                    # untested 
                    url = '%s/%s' % (self.portal_url, attr[1][attr[1].find('resolveuid/'):])
                elif attr[1].startswith('#'):
                    url = attr[1]
                else:
                    logger.info("href main branch code")
                    try:
                        # split anchor from url
                        baseurl, anchor = urlparse.urldefrag(attr[1])
                        o = self.context.restrictedTraverse(urllib.unquote(baseurl))
                        if getattr(o, 'absolute_url', None):
                            url = o.absolute_url()
                        else:
                            # maybe we got a view instead of an traversal object:
                            if getattr(o, 'context', None):
                                url = o.context.absolute_url()
                            else:
                                url = attr[1]
                        if anchor:
                            url = '#' + anchor
                    except:
                        url = attr[1]
                if isinstance(url, unicode):
                    url = url.encode(self.encoding)
                self.html += ' href="%s"' % url
            else:
                self.html += ' %s="%s"' % (attr)

        self.html += ">"

    def handle_endtag(self, tag):
        """
        """
        self.html += "</%s>" % tag

    def handle_data(self, data):
        """
        """
        self.html += data

    def handle_charref(self, name):
        self.html += "&#%s;" % name

    def handle_entityref(self, name):
        self.html += "&%s;" % name

    def handle_comment(self, data):
        self.html += "<!--%s-->" % data

    def handle_decl(self, decl):
        self.html += "<!%s>" % decl

    def handle_startendtag(self, tag, attrs):
        """
        """
        self.html += "<%s" % tag
        for attr in attrs:
            if attr[0] == "src":
                url_tuple = urlparse.urlsplit(attr[1])
                url = None
                if url_tuple.scheme != '':
                    url = attr[1]
                elif url_tuple.path.startswith('/'):
                    url = '%s%s' % (self.portal_url, attr[1])
                elif url_tuple.path.startswith('resolveuid/'):
                    # consider resolveuid url as absolute
                    # on sept 2011, TinyMCE create img src as "resolveuid/..." 
                    url = '%s/%s' % (self.portal_url, attr[1])
                elif 'resolveuid/' in url_tuple.path:
                    # see href
                    url = '%s/%s' % (self.portal_url, attr[1][attr[1].find('resolveuid/'):])
                else:
                    logger.info("src main branch code for embedding image")
                    self.html += ' src="cid:image_%s"' % self.image_number
                    self.image_number += 1
                    self.image_urls.append(attr[1])
                if url is not None:
                    self.html += ' src="%s"' % url
            else:
                self.html += ' %s="%s"' % (attr)

        self.html += " />"
