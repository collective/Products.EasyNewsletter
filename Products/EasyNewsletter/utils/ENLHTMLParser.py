import HTMLParser
from Products.CMFCore.utils import getToolByName
import re

class ENLHTMLParser(HTMLParser.HTMLParser):
    """A simple parser which exchange relative URLs with obsolute ones"""
   
    def __init__(self, context, cid_images=False):
       
        self.context = context
        self.html = ""
        self.image_objs = []
        self.image_number = 0
        self.cid_images = cid_images
       
        HTMLParser.HTMLParser.__init__(self)

    def _resolveObject(self, url, object=True):
        value = None
        try:
            value = self.context.restrictedTraverse(url)
            if not object:
                value = value.absolute_url()
        except:
            value = self._resolve_uid_link(url, object)

        return value

    def _resolve_uid_link(self, url, object=False):
        """ handle the resolveuid urls """
        UIDURL = re.compile("resolveuid/([^/]+)(.*?)$")
        uid_catalog = getToolByName(self.context, 'uid_catalog')
        obj = None
        match = UIDURL.search(url)
        if match:
            # src=http://someurl/resolveuid/<uid>
            uid = match.group(1)
            img_suffix = match.group(2)
            brains = uid_catalog(UID=uid)
            if len(brains):
                obj = brains[0].getObject()
                url = "%s%s" % (obj.absolute_url(), img_suffix)
                if object:
                    obj = obj.restrictedTraverse(img_suffix[1:])

        if object:
            return obj
        else:
            return url

                
    def handle_starttag(self, tag, attrs):
        """
       """

        self.html += "<%s" % tag
        for attr in attrs:
            if attr[0] == "href":
                url = self._resolveObject(attr[1], object=False)
               
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
       
    def handle_startendtag(self, tag, attrs):
        """
       """
        self.html += "<%s" % tag
        for attr in attrs:
            if attr[0] == "src":
                if self.cid_images:
                    self.html += ' src="cid:image_%s"' % self.image_number
                    self.image_number += 1
                    o = self._resolveObject(attr[1], object=True)
                    self.image_objs.append(o)
                else:
                    url = self._resolveObject(attr[1], object=False)
                    self.html += ' src="%s"' % url
            else:
                self.html += ' %s="%s"' % (attr)
      
        self.html += " />"
       
