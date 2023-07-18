__all__ = [ 'CharsetHTMLParser', 'ImageLinkHTMLParser', 'MediaHMTLParser' ]

# logging
import logging
log = logging.getLogger(__name__)
log.debug('MODULE {}'.format(__name__))

import html.parser
import lxml.html

# --------------------------------------------------------------------

class ImageLinkHTMLParser :

    def __init__(self) :
        self._images_links = {}

    def parse(self, data) :
        self._images_links = {}
        tree = lxml.html.fromstring(data)
        self._images_links.update(zip(
            tree.xpath("//a[descendant::img]/descendant::img/@src"),
            tree.xpath("//a[descendant::img]/@href")
        ))
        self._images_links.update(zip(
            tree.xpath("//div[*/img]//img/@src"),
            tree.xpath("//div[*/img]/following-sibling::a/@href")
        ))

    @property
    def images(self) :
        return list(self.images_links.keys())

    @property
    def links(self) :
        return list(self.images_links.values())

    @property
    def images_links(self) :
        try :
            il = self._images_links
        except AttributeError :
            il = {}
        return il

# --------------------------------------------------------------------

class CharsetHTMLParser(html.parser.HTMLParser) :

    def parse(self, data) :
        self._content = []
        for line in data.splitlines() :
            self.feed(line.decode('utf-8'))
            if len(self._content) > 0 :
                break

    @property
    def charset(self) :
        try :
            return self._content[0]
        except IndexError :
            return 'utf-8'

    def handle_starttag(self, tag, attrs) :
        attributes = dict(attrs)
        if ( tag == 'meta' and 'http-equiv' in attributes
             and 'content' in attributes ) :
            if 'charset' in attributes['content'] :
                self._content.append(attributes['content'].split('=').pop())
            

# --------------------------------------------------------------------

class MediaHTMLParser(html.parser.HTMLParser) :

    def parse(self, data) :
        self._images_links = {}
        self._linkopen = False        
        self.feed(data)

    @property
    def images(self) :
        return list(self.images_links.keys())

    @property
    def links(self) :
        return list(self.images_links.values())

    @property
    def images_links(self) :
        try :
            il = self._images_links
        except AttributeError :
            il = {}
        return il

    def handle_starttag(self, tag, attrs) :
        attributes = dict(attrs)
        if tag == 'a' and 'href' in attributes :
            log.debug(f"<a> : href={attributes['href']}")
            self._linkopen = attributes['href']

        if tag == 'div' and 'style' in attributes :
            log.debug(f"<div> : style={attributes['style']}")
            if 'background-image:url(' in attributes['style'] :
                if self._linkopen is not None :
                    image = attributes['style'].split('(')[-1].split(')')[0]
                    log.info(f"background-image:url = {image} => link href={self._linkopen}")
                    self._images_links[image] = self._linkopen
            
        if tag == 'img' and 'src' in attributes :
            log.debug(f"<img> : src={attributes['src']}")
            if self._linkopen is not None :
                log.info(f"image src={attributes['src']} => link href={self._linkopen}")
                self._images_links[attributes['src']] = self._linkopen

    def handle_endtag(self, tag) :
        if tag == 'a' :
            self._linkopen = None
            log.debug(f"<a> END")

# --------------------------------------------------------------------
    
