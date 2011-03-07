import HTMLParser
import urlparse
import urllib

class ENLHTMLParser(HTMLParser.HTMLParser):
    """A simple parser which exchange relative URLs with obsolute ones"""
    
    def __init__(self, context):
        
        self.context = context
        self.html = ""
        self.image_urls = []
        self.image_number = 0
        
        HTMLParser.HTMLParser.__init__(self)
                 
    def handle_starttag(self, tag, attrs):
        """
        """
        self.html += "<%s" % tag
        
        
        for attr in attrs:
            if attr[0] == "href":
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
                        url += '#' + anchor
                except:
                    url = attr[1]
                
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
                self.html += ' src="cid:image_%s"' % self.image_number
                self.image_number += 1
                self.image_urls.append(attr[1])
            else:
                self.html += ' %s="%s"' % (attr)
           
        self.html += " />"
        
