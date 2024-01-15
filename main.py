# -*- encoding: utf-8 -*-
from __future__ import (
    absolute_import,
    print_function, division,
    unicode_literals
)

# Paramètres ligne de commande
import logging
import argparse
import os

# Tkinter
try : # python 3.x
    import tkinter as tk
    import tkinter.ttk as ttk
except : # python 2.x
    import Tkinter as tk
    import ttk

# Configuration
import __main__ as locator
from pk_config import config

# Services
from pk_services.exceptions import ServiceError
from pk_services.core import Tor
from pk_services.web import GrabService
from pk_services.youtube import YoutubeService

# Helpers
from helpers.video import Video

# Widgets
import core.elements
from widgets.gallery import GalleryFrame
from widgets.window import ImageWindow

# ------------------------------------------------------------------------------

class Application(tk.Tk, object) :

    def __init__(self, conf, options) :
        super(Application, self).__init__()
        self.conf = conf
        self.options = options

        self.configureService()
        self.youtube = YoutubeService()
        self.formats = self.conf.get_json('formats', {})
        self.task_cancel = False
        self.createWidgets()

    def configureService(self) :
        self.service = GrabService()
        self.service.user_agent = self.conf.get('User-Agent')
        self.service.parser.config.update(self.conf.get_json('domains'))
        self.service.ext = ('jpg', 'jpeg')
        self.service.head = self.options.head
        
    def createWidgets(self) :
        # toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X)

        # clear
        ttk.Button(
            toolbar,
            text='clear', command=self.clear
        ).pack(
            side=tk.LEFT
        )
        # stopload
        ttk.Button(
            toolbar,
            text='stop', command=self.loadstop
        ).pack(
            side=tk.LEFT
        )
        # update + load
        ttk.Button(
            toolbar,
            text='update/load', command=self.update
        ).pack(
            side=tk.LEFT
        )
        # refresh
        ttk.Button(
            toolbar,
            text='refresh', command=self.reload
        ).pack(
            side=tk.LEFT
        )

        # gallery cols
        self.cols = tk.IntVar()
        spinBox = tk.Spinbox(
            toolbar,
            width=5,
            from_=3, to=8,
            textvariable=self.cols, command=self.reorg)
        spinBox.pack(side=tk.LEFT)
        self.cols.set(5)

        # change url
        self.url = tk.StringVar()
        url_change = self.register(self.url_change)
        ttk.Entry(
            toolbar,
            width=42,
            textvariable=self.url,
            validate='all',
            validatecommand=(url_change, '%V', '%s', '%P'),
        ).pack(
            side=tk.LEFT
        )
        self.url.set(self.options.url)

        # extensions
        self.extensions = tk.StringVar()
        ext_change = self.register(self.ext_change)
        ttk.Entry(
            toolbar,
            width=12,
            textvariable=self.extensions,
            validate='all',
            validatecommand=(ext_change, '%V', '%s', '%P'),
        ).pack(
            side=tk.LEFT
        )
        self.extensions.set(self.service.ext)

        # modify the format for build_url
        self.format = tk.StringVar()
        ttk.Entry(
            toolbar,
            width=20,
            textvariable=self.format
        ).pack(
            side=tk.LEFT
        )
        self.format.set(
            self.formats.get(GrabService.domain(self.options.url), '')
        )

        # checkbox Tor
        self._useTor = tk.BooleanVar()
        ttk.Checkbutton(
            toolbar,
            text='Tor', command=self.toggle_tor,
            var=self._useTor,
            onvalue=True,
            offvalue=False
        ).pack(
            side=tk.LEFT
        )
        self._useTor.set(Tor.isEnabled())

        # checkbox Native
        self._native = tk.BooleanVar()
        ttk.Checkbutton(
            toolbar,
            text='native',
            var=self._native,
            onvalue=True,
            offvalue=False
        ).pack(
            side=tk.LEFT
        )
        self._native.set(self.options.native)

        # checkbox Usedb
        self._usedb = tk.BooleanVar()
        ttk.Checkbutton(
            toolbar,
            text='use',
            var=self._usedb,
            onvalue=True,
            offvalue=False
        ).pack(
            side=tk.LEFT
        )
        self._usedb.set(False)

        # [db] : save format for current url domain
        ttk.Button(
            toolbar,
            width=3,
            text='db', command=self.save_format
        ).pack(
            side=tk.LEFT
        )        

        # status bar
        self.status = ttk.Label(toolbar, text='<status>', background='cornflowerblue', width=20)
        self.status.pack(side=tk.LEFT, fill=tk.X)

        # status bar yt
        self.status_yt = ttk.Label(toolbar, text='<video>', background='darkseagreen', width=20)
        self.status_yt.pack(side=tk.LEFT, fill=tk.X)        

        # gallery
        self.gal = GalleryFrame(
            self,
            thumbsize=(256, 192),
            rows=3.5, cols=self.cols.get()
        )
        self.gal.pack(fill=tk.BOTH, expand=True)

        # Action on thumbnail click
        self.bind('<<ClickThumb>>', self.click_thumb)
        self.bind('<<MiddleClickThumb>>', self.middle_click_thumb)
        self.bind('<<RightClickThumb>>', self.right_click_thumb)

    def loadstop(self) :
        self.task_cancel = True
        logging.info('stop')
        self.status.config(text='stopped')
                
    def clear(self) :
        self.task_cancel = True
        logging.info('clear')
        self.status.config(text='')
        self.gal.clear()

    def load(self) :
        logging.info('load in progress')
        self.clear()
        self.task_cancel = False
        if self.options.images :
            logging.info('load images in progress')
            self.status.config(text='work in progress...')
            for image in self.service.images :
                if self.task_cancel :
                    break
                try :
                    link = self.service.images_links[image]
                    logging.debug(f"load: link={link}")
                    basename = link.rstrip('/').rpartition('/')[-1]
                    logging.debug(f"load: basename={basename}")
                    title = basename.split('.')[0]
                except :
                    title = 'title'
                logging.debug(f"load: title={title}")
                self.gal.append(image, title)
            logging.info('load images done')
            self.status.config(text='images done.')
        if self.options.links :
            logging.info('load links in progress')
            self.status.config(text='work in progress...')
            for link in self.service.links :
                if self.task_cancel :
                    break
                self.gal.append(link)
            logging.info('load links done')
            self.status.config(text='links done.')

    def update(self) :
        logging.info('update in progress')
        self.status.config(text='work in progress...')
        self.service.url = self.url.get()
        #self.service.update()
        logging.info('update done')
        self.status.config(text='update done.')
        self.load()

    def reload(self) :
        logging.info('reload in progress')
        self.status.config(text='work in progress...')
        self.gal.reload()
        logging.info('reload done')
        self.status.config(text='reload done')

    def reorg(self) :
        self.gal.cols = self.cols.get()
            
    def url_change(self, reason, past, future) :
        new_dom = GrabService.domain(future)
        fmt = self.formats.get(new_dom, '')
        self.format.set(fmt)
        if reason in ('focusout') :
            if future != self.service.url :
                try :
                    self.service.url = future
                    self.status.config(text='Url ok')
                except ServiceError as e :
                    logging.error('url={} : {}'.format(future, e))
                    self.status.config(text='Url {}'.format(e))
        return True

    def ext_change(self, reason, past, future) :
        self.service.ext = (e.strip() for e in future.split())
        logging.debug(
            'ext_change: reason={} past={} future={} ext={}'.format(
            reason, past, future, self.service.ext
            )
        )
        return True

    def toggle_tor(self) :
        logging.info(f'toggle_tor: Tor enabled = {self._useTor.get()}')
        if self._useTor.get() :
            Tor.enable()
        else :
            Tor.disable()

    def save_format(self) :
        dom = GrabService.domain(self.url.get())
        self.formats[dom] = self.format.get()
        self.conf.add_json('formats', self.formats)

    def build_url(self, source) :
        logging.debug('use_db : {}'.format(self._usedb.get()))
        if self._usedb.get() :
            logging.debug('source : {}'.format(source))
            data = [ source, self.service.base ]
            data.extend(source.replace('.','/').split('/'))
            built_url = self.format.get().format(*data)
        else :
            built_url = self.service.images_links[source]
        logging.info(
            'built_url: {}'.format(
                built_url,
            )
        )
        return built_url

    def click_thumb(self, event=None) :
        for image in self.gal.find_withid(event.state) :
            ImageWindow(
                self, source=image, closeFunc=lambda widget : True
            ).lift()
            logging.info(
                '{}'.format(
                    image.source
                )
            )

    def middle_click_thumb(self, event=None) :
        self.format_sort = f"res:1080,+tbr"
        for image in self.gal.find_withid(event.state) :
            self.spawn_video(image, player='mpv')

    def right_click_thumb(self, event=None) :
        self.format_sort = f"res:720,+tbr"
        for image in self.gal.find_withid(event.state) :
            self.spawn_video(image, player='mpv')

    def spawn_video(self, image, player=None) :
        built_url = self.build_url(image.source)
        logging.info(f"spawn_video : {built_url}")

        message = built_url.rstrip('/').split('/')[-1]
        self.youtube = YoutubeService(format_sort=self.format_sort)
        self.youtube.url = built_url
        if self.youtube['error'] is not None :
            logging.error(f"spawn_video : {message} {self.youtube['error']}")
            self.status_yt.config(text=message, background='orange')
            return
        title = self.youtube.title
        video_url = self.youtube['url']

        logging.debug(f'spawn_video : url  - {self.youtube.url}')
        logging.debug(f'spawn_video : _url - {self.youtube._url}')
        logging.debug(f'spawn_video : format_sort - {self.youtube.format_sort}')
        for fmt in self.youtube.get_formats() :
            logging.debug(f'spawn_video : format      - {fmt}')
        logging.debug(f'spawn_video : selected_formats - {self.youtube.selected_formats}')
        logging.debug(f'spawn_video : video_url  - {video_url}')
        logging.debug(f'spawn_video : title      - {title}')
        logging.debug(f'spawn_video : resolution - {self.youtube.resolution}')
            
        self.status_yt.config(text=message, background='darkseagreen')            

        if self._native.get() :
            logging.debug(f'spawn_video : native - title = {title}')
            logging.debug(f'spawn_video : native - video_url = {video_url}')
            video = Video(video_url, titre=title, filtre=self.format_sort)
        else :
            logging.debug(f'spawn_video : built - title = {title}')
            logging.debug(f'spawn_video : built - built_url = {built_url}')
            logging.debug(f'spawn_video : built - video_url = {video_url}')
            video = Video(built_url, titre=title, filtre=self.format_sort)

        video.player = player
        proc = video.play()
        logging.info(f'spawn_video : play - player = {video.player.__class__.__name__}')
        logging.info(f'spawn_video : play - pid = {proc.pid}')
        logging.info(f'spawn_video : play - titre = {video._titre}')
        logging.info(f'spawn_video : play - uri = {video._uri}')
        

# ------------------------------------------------------------------------------

def parse_args() :
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser_group = parser.add_mutually_exclusive_group(required=False)
    parser.add_argument(
        'url',
        nargs='?',
        default='https://',
    )
    parser_group.add_argument(
        '-I', '--images',
        action='store_true',
        help='capture embedded images'
    )
    parser_group.add_argument(
        '-K', '--links',
        action='store_true',
        help='capture linked images'
    )
    parser_group.add_argument(
        '-N', '--native',
        action='store_true',
        help='native video or ytdl'
    )
    parser.add_argument(
        '-H', '--head',
        default='.*',
        help='head filename filter'
    )
    parser.add_argument(
        '-L', '--loglevel',
        default='WARNING',
        #default='INFO',
        #default='DEBUG',
        help='log level'
    )
    args = parser.parse_args()
    if not args.links :
        args.images = True

    return args

# ------------------------------------------------------------------------------

def main() :

    # Command line parameters
    args = parse_args()

    # Logging
    logging.basicConfig(level=args.loglevel)
    logging.info('start logging')
    logging.info('args=%r', args)

    # Configuration
    prj_database = config.project_database(locator)
    conf = config.Configuration(prj_database)
    logging.info(conf.database)
    assert conf.checklist(['User-Agent'])
    core.elements.Image.webRequest.user_agent = conf.get('User-Agent')

    # User Interface and mainloop
    app = Application(conf=conf, options=args)
    app.geometry('1366x768-20+10')
    app.mainloop()

# ------------------------------------------------------------------------------

if __name__ == '__main__' :
    main()
