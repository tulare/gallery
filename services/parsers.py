# -*- encoding: utf-8 -*-
from __future__ import (
    absolute_import,
    print_function, division,
    unicode_literals
)

__all__ = [ 'CharsetHTMLParser', 'MediaHMTLParser' ]

# logging
import logging
log = logging.getLogger(__name__)
log.debug('MODULE {}'.format(__name__))

try : # python 2.7
    import HTMLParser as htmlparser
except ImportError :
    import html.parser as htmlparser

# --------------------------------------------------------------------

class CharsetHTMLParser(htmlparser.HTMLParser, object) :

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

class MediaHTMLParser(htmlparser.HTMLParser, object) :

    def parse(self, data) :
        self._images_links = {}
        #self._images = []
        #self._links = []
        self._linkopen = False
        
        self.feed(data)

    @property
    def images(self) :
        return list(self._images_links.keys())

    @property
    def links(self) :
        return list(self._images_links.values())

    @property
    def images_links(self) :
        return self._images_links

    def handle_starttag(self, tag, attrs) :
        attributes = dict(attrs)
        if tag == 'a' and 'href' in attributes :
            log.debug("start tag : {} href={}".format(tag, attributes['href']))
            self._linkopen = attributes['href']

        if tag == 'div' and 'style' in attributes :
            log.debug("start tag : {} style={}".format(tag, attributes['style']))
            if 'background-image:url(' in attributes['style'] :
                if self._linkopen is not None :
                    image = attributes['style'].split('(')[-1].split(')')[0]
                    log.info("background-image:url = {}".format(image))
                    self._images_links[image] = self._linkopen
            
        if tag == 'img' and 'src' in attributes :
            log.debug("start tag : {} src={}".format(tag, attributes['src']))
            if self._linkopen is not None :
                log.info("image src={}".format(attributes['src']))
                self._images_links[attributes['src']] = self._linkopen

    def handle_endtag(self, tag) :
        if tag == 'a' :
            self._linkopen = None
            log.debug("end tag : {}".format(tag))

# --------------------------------------------------------------------
