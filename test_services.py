# Logging
import logging
logging.basicConfig(level=logging.DEBUG)

import re
import msvcrt
import urllib.parse

# Configuration
import __main__ as locator
from pk_config import config

from services.core import Tor
from services.web import WebService, GrabService
from services.youtube import YoutubeService
from services.players import MediaPlayer
from helpers.video import Video

def play_link(indice) :
    print(gs.links[indice])
    yt.url = gs.links[indice].split('#')[0]
    print(yt.title)
    v = Video(yt.get_format()['url'], yt.title)
    p = v.play()
    p.wait()

def images_links(url) :
    result = {}

    resp = ws.opener.open(url)
    data = resp.read()
    images = re.findall(b'<img [^<]+/>', data)
    for img in images :
        try :
            idx_img = data.index(img)
            idx_src = data.index(b'src="', idx_img)
            idx_src_end = data.index(b'"', idx_src + 5)
            image = urllib.parse.urljoin(resp.url, f'{data[idx_src+5:idx_src_end].decode()}')
            idx_href = data.index(b'href="', idx_src)
            idx_href_end = data.index(b'"', idx_href + 6)
            link = urllib.parse.urljoin(resp.url, f'{data[idx_href+6:idx_href_end].decode()}')
            result[image] = link
        except :
            pass
    return result


def play_list(url) :
    il = images_links(url)

    for clip in il :
        try :
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
    
