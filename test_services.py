# Logging
import logging
logging.basicConfig(level=logging.DEBUG)

import re
import msvcrt
import urllib.parse
import lxml.html

# Configuration
import __main__ as locator
from pk_config import config

from services.core import Tor
from services.parsers import CharsetHTMLParser, ImageLinkHTMLParser, MediaHTMLParser
from services.web import WebService, GrabService
from services.youtube import YoutubeService
from services.players import MediaPlayer
from helpers.video import Video

class Page :

    def __init__(self, url) :
        self.url_charge(url)        

    def __repr__(self) :
        cls = self.__class__.__name__
        return f"{cls}(url='{self.url}')"

    def url_charge(self, url) :
        ws = WebService()
        ws.user_agent = conf.get('User-Agent')
        req = ws.opener.open(url)
        bindata = req.read()
        charset_parser = CharsetHTMLParser()
        charset_parser.parse(bindata)
        data = bindata.decode(charset_parser.charset)
        self._page = {
            'url' : req.url,
            'data' : data,
            'tree' : lxml.html.fromstring(data)
        }

    @property
    def url(self) :
        return self._page['url']

    @url.setter
    def url(self, url) :
        self.url_charge(url)

    @property
    def data(self) :
        return self._page['data']

    @property
    def tree(self) :
        return self._page['tree']

    @property
    def images_links(self) :
        parser = ImageLinkHTMLParser()
        parser.parse(self.data)
        result = dict(zip(
            map(lambda url : urllib.parse.urljoin(self.url, url), parser.images),
            map(lambda url : urllib.parse.urljoin(self.url, url), parser.links)
        ))
        return result

    @property
    def media_images_links(self) :
        parser = MediaHTMLParser()
        parser.parse(self.data)
        result = dict(zip(
            map(lambda url : urllib.parse.urljoin(self.url, url), parser.images),
            map(lambda url : urllib.parse.urljoin(self.url, url), parser.links)
        ))
        return result
                
def play_link(indice) :
    print(gs.links[indice])
    yt.url = gs.links[indice]
    print(yt.title)
    p = mpv.play(yt.title, yt.url)
    p.wait()

def play_list(url) :
    page = Page(url)
    il = page.images_links

    for clip in il :
        try :
            print(il)
            yt.url = il[clip]
            #v = Video(*reversed(yt.video(720)))
            p = mpv.play(yt.title, yt.url)
            p.wait()
        except :
            pass
        keypress = msvcrt.getch()
        if keypress == b'\x1b' :
            break
        if keypress == b'n' :
            continue

if __name__ == "__main__" :

    # Logging
    logging.info('start logging')
    
    # Configuration
    prj_database = config.project_database(locator)
    conf = config.Configuration(prj_database)

    #Tor.enable()

    ws = WebService()
    ws.user_agent = conf.get('User-Agent')
    
    gs = GrabService()
    gs.user_agent = conf.get('User-Agent')
    gs.ext = 'jpg','jpeg','png'

    yt = YoutubeService()

    mpv = MediaPlayer(id='mpv')
    mpv.program = 'mpv.com'
    
