# -*- coding: utf-8 -*-

# Logging
import logging
logging.basicConfig(level=logging.DEBUG)

import re
import pathlib
import subprocess
import msvcrt
import json
import urllib.parse
import lxml.etree

# Configuration
import __main__ as locator
from pk_config import config

# Test Gallery
import tkinter as tk
from widgets.gallery import GalleryFrame

from pk_services.core import Tor
from pk_services.parsers import DomainParserConfig, CharsetHTMLParser, ImageLinkHTMLParser, MediaHTMLParser
from pk_services.web import WebService, GrabService
from pk_services.youtube import YoutubeService
from pk_services.players import MediaPlayer
from helpers.video import Video

def importDomainsTo(conf) :
    dp = DomainParserConfig()
    dp.loadJSON('domains.json')
    conf.add('domains', dp.toJSON())
    return dp

def exportDomainsFrom(conf) :
    dp = DomainParserConfig()
    dp.update(conf.get_json('domains'))
    dp.saveJSON('domains.json')
    return dp

class Page :

    def __init__(self, url, *, charset_fallback='latin-1') :
        self.parser = ImageLinkHTMLParser()
        self.parser.config.loadJSON('domains.json')
        self._charset_fallback = charset_fallback
        self.url_charge(url)

    def __repr__(self) :
        cls = self.__class__.__name__
        return f"{cls}(url='{self.url}')"

    def recharge(self) :
        self.url_charge(self.url)

    def url_charge(self, url) :
        ws = WebService()
        ws.user_agent = conf.get('User-Agent')
        req = ws.opener.open(url)
        bindata = req.read()
        charset_parser = CharsetHTMLParser()
        charset_parser.parse(bindata)
        try :
            data = bindata.decode(charset_parser.charset)
        except UnicodeDecodeError :
            data = bindata.decode(self._charset_fallback)
        self._page = {
            'url' : req.url,
            'data' : data,
            'tree' : lxml.etree.HTML(data)
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
        self.parser.parse(self.data, self.url)
        result = dict(map(
            lambda url : (
                urllib.parse.urljoin(self.url, url[0]),
                urllib.parse.urljoin(self.url, url[1])
            ),
            self.parser.images_links.items()
        ))
        return result

    @property
    def imgbox_images(self) :
        result = [
            (index, f"{thumb.replace('thumbs','images').replace('_b.','_o.')}")
            for index, thumb in enumerate(p.images_links)
        ]
        return result

    @property
    def media_images_links(self) :
        parser = MediaHTMLParser()
        parser.parse(self.data)
        result = dict(map(
            lambda url : (
                urllib.parse.urljoin(self.url, url[0]),
                urllib.parse.urljoin(self.url, url[1])
            ),
            parser.images_links.items()
        ))
        return result

    def get_images_links(self, domain_parser_config=None) :
        if domain_parser_config is None :
            domain_parser_config = self.parser.config
        motif_img, motif_link = domain_parser_config.find_url(self.url)
        result = dict(zip(
            map(
                lambda url : urllib.parse.urljoin(self.url, url),
                self.tree.xpath(motif_img)
                ),
            map(
                lambda url : urllib.parse.urljoin(self.url, url),
                self.tree.xpath(motif_link)
                )
            )
        )
        return result

    def gallery(self) :
        root = tk.Tk()
        gal = GalleryFrame(root, rows=3, cols=7)
        gal.pack(fill=tk.BOTH, expand=True)
        imlk = self.images_links
        for image in imlk :
            gal.append(image, imlk[image])
        root.mainloop()
    
    def play_link(self, indice) :
        imlk = self.images_links
        play_link(list(imlk.values()), indice)


# ------------------------------------------------------------------------------

def play_link(links, indice) :
    print(links[indice])
    yt.url = links[indice]
    print(yt.title)
    p = mpv.play(yt.title, yt.url)
    p.wait()

# ------------------------------------------------------------------------------

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
# ------------------------------------------------------------------------------

def show_gallery(page=None) :
    root = tk.Tk()
    gal = GalleryFrame(root, rows=3, cols=7)
    gal.pack(fill=tk.BOTH, expand=True)

    if page is not None :
        il = page.images_links
        for image in il :
            gal.append(image, il[image])

    root.mainloop()

# ------------------------------------------------------------------------------

class CurlPage :

    def __init__(self, url, *, encoding='utf-8', use_tor=False, outdir='.') :
        self._encoding = encoding
        self._use_tor = use_tor
        self._outdir = outdir
        self.url = url

    def update(self) :
        try :
            self._page = curl_tree(self._url, encoding=self._encoding, use_tor=self._use_tor)
        except OSError as e :
            self._page = { 'data' : e }

    @property
    def url(self) :
        return self._url

    @url.setter
    def url(self, url) :
        self._url = url
        self.update()

    @property
    def data(self) :
        return self._page.get('data')

    @property
    def tree(self) :
        return self._page.get('tree')

    @property
    def use_tor(self) :
        return self._use_tor

    @use_tor.setter
    def use_tor(self, value) :
        self._use_tor = bool(value)

    @property
    def box_title(self) :
        return self.tree.xpath('//h1/text()')[0]

    @property
    def box_images(self) :
        result = [
            (index, f"{thumb.replace('thumbs','images').replace('_b.','_o.')}")
            for index, thumb in enumerate(self.tree.xpath("//a[descendant::img]/descendant::img/@src"))
        ]
        return result


    def box_download(self, image) :
        try :
            indice, url_image = image
            curl_download(url_image, outdir=self._outdir, filename=f"{indice:03d}", use_tor=self.use_tor)
        except IndexError as e :
            logging.error(e)
            return
        except OSError as e :
            logging.error(e)
            return

    @property
    def bam_images(self) :
        bam_data = ''.join(self.tree.xpath("//input[contains(@value,'alt=')]/@value"))
        bam_tree = lxml.etree.HTML(bam_data)
        result = list()
        for image in bam_tree.xpath('//a[descendant::img[@alt!=""]]') :
            index = image.xpath('img/@alt')[0]
            result.append((index, image.attrib['href']))
        return result

    def bam_download(self, image) :
        try :
            nom_image, url_image = image
            page = curl_tree(url_image, encoding=self._encoding, use_tor=self.use_tor, cookie='nsfw_inter=1')
            url_download = page['tree'].xpath(f'//img[@alt="{nom_image}"]/@src')[0]
            logging.debug(url_download)
            curl_download(url_download, outdir=self._outdir, filename=nom_image, use_tor=self.use_tor)
        except IndexError as e :
            logging.error(e)
            return
        except OSError as e :
            logging.error(e)
            return
        
# ------------------------------------------------------------------------------

def curl_tree(url, *, encoding='utf-8', use_tor=False, cookie=None) :

    # contruire la commande url
    curl_command = [ 'curl', '--ssl-no-revoke' ]
    if cookie is not None :
        curl_command.extend(['--cookie', cookie])
    if use_tor :
        curl_command.extend(['--socks5-hostname', 'localhost:9150'])
    curl_command.extend([f'{url}'])
    logging.debug(curl_command)

    try :
        data = subprocess.check_output(curl_command, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e :
        logging.error(e)
        raise OSError(e)

    return {
        'url' : url,
        'data' : data.decode(encoding),
        'tree' : lxml.etree.HTML(data)
    }

# ------------------------------------------------------------------------------

def curl_download(url, outdir='.', filename=None, use_tor=False) :

    # chemin relatif url
    url_path = pathlib.Path(urllib.parse.urlparse(url).path)

    # répertoire de sortie
    output_dir = pathlib.Path(outdir)
    if not output_dir.exists() :
        output_dir.mkdir()
    elif not output_dir.is_dir() :
        raise OSError(f"{output_dir} existe mais ce n'est pas un répertoire")

    # fichier de sortie
    output_file = output_dir / url_path.name
    if filename is not None :
        filename = pathlib.Path(filename)
        output_file = output_file.with_name(f'{filename.stem}_{url_path.name}')
    
    # construire la commande curl
    curl_command = [ 'curl', '--ssl-no-revoke' ]
    if use_tor :
        curl_command.extend(['--socks5-hostname', 'localhost:9150'])
    curl_command.extend([f'{url}', '--output', f'{output_file}'])
    logging.debug(curl_command)

    # exécuter la commande
    try :
        subprocess.check_call(curl_command)
    except subprocess.CalledProcessError as e :
        raise OSError(e)

# ------------------------------------------------------------------------------

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
    
