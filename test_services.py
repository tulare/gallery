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
from helpers.curl import CurlEngine, PageHTML, site_url, force_https

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

    def __init__(self, url, *, use_tor=False, circuit=None, outdir='.') :
        self._curl = CurlEngine(use_tor=use_tor, circuit=circuit)
        self.outdir = outdir
        self.url = url

    def update(self) :
        try :
            self._page = self.curl.load(self._url)
        except OSError as e :
            self._page = PageHTML({ 'source' : e })

    @property
    def curl(self) :
        return self._curl

    @property
    def url(self) :
        return self._url

    @url.setter
    def url(self, url) :
        self._url = url
        self.update()

    @property
    def outdir(self) :
        return self._outdir

    @outdir.setter
    def outdir(self, outdir) :
        self._outdir = pathlib.Path(outdir)

    @property
    def site(self) :
        return site_url(self.url)

    @property
    def source(self) :
        return self._page.source

    @property
    def tree(self) :
        return self._page.tree

    @property
    def ibox_title(self) :
        return self.tree.xpath('//h1/text()')[0]

    @property
    def ibox_images(self) :
        result = [
            (f"{index:03d}", urllib.parse.urljoin(self.url, thumb))
             for index, thumb in enumerate(self.tree.xpath("//a[img[@src]]/@href"))
        ]
        return result

    @property
    def icloud_images(self) :
        result = [
            (f"{index:03d}", urllib.parse.urljoin(self.url, thumb))
             for index, thumb in enumerate(self.tree.xpath("//a[img[@src]]/@href"))
        ]
        return result

    @property
    def ibam_images(self) :
        bam_data = ''.join(self.tree.xpath("//input[contains(@value,'alt=')]/@value"))
        bam_tree = lxml.etree.HTML(bam_data)
        result = list()
        for image in bam_tree.xpath('//a[descendant::img[@alt!=""]]') :
            index = image.xpath('img/@alt')[0]
            result.append((index, image.attrib['href']))
        return result

    @property
    def erop_images(self) :
        result = [
            (f"{(index+1):03d}", force_https(urllib.parse.urljoin(self.url, thumb)))
            for index, thumb in enumerate(self.tree.xpath('//a[img][@target="_blank"]/@href'))
        ]
        return result

    def download(self, image) :
        nom_image, url_image = image

        # gestion des cookies ?
        if site_url(url_image) in ('www.imagebam.com', ) :
            self.curl.cookie = 'nsfw_inter=1'
        else :
            self.curl.cookie = None
        logging.debug(f"{nom_image}, {url_image}")

        # récupération url et téléchargement
        try :
            page = self.curl.load(url_image)
            url_download = self.resolve_url(page)
            self.curl.download(url_download, outdir=self.outdir, filename=nom_image)
        except OSError as e :
            logging.error(e)
            return

    def resolve_url(self, page) :
        site = urllib.parse.urlparse(page.url).netloc
        logging.debug(f'site: {site}')
        if site in ('imgcloud.pw', 'imgbox.com', 'www.turboimagehost.com', ) :
            url_download = page.tree.xpath("//meta[@property='og:image']/@content")
        elif site in ('www.imagebam.com', ) :
            url_download = page.tree.xpath("//img[contains(@class,'main-image')]/@src")
        elif site in ('pixhost.to', ) :
            url_download = page.tree.xpath("//img[@id='image']/@src")
        elif site in ('postimg.cc', ) :
            url_download = page.tree.xpath("//a[@id='download']/@href")
        else :
            raise OSError(f"site error: {site}")

        try :
            url_download = force_https(url_download[0])
            logging.debug(url_download)
        except IndexError as e :
            raise OSError(e)

        return url_download
        
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
    
