# -*- encoding: utf-8 -*-
from __future__ import (
    absolute_import,
    print_function, division,
    unicode_literals
)

# Paramètres ligne de commande
import logging
import argparse

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
        self.service.ext = self.options.ext
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
        # load
        ttk.Button(
            toolbar,
            text='load', command=self.load
        ).pack(
            side=tk.LEFT
        )
        # update + load
        ttk.Button(
            toolbar,
            text='update + load', command=self.update
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
            from_=3, to=8,
            textvariable=self.cols, command=self.reorg)
        spinBox.pack(side=tk.LEFT)
        self.cols.set(5)

        # change url
        self.url = tk.StringVar()
        url_change = self.register(self.url_change)
        ttk.Entry(
            toolbar,
            width=50,
            textvariable=self.url,
            validate='all',
            validatecommand=(url_change, '%V', '%s', '%P'),
        ).pack(
            side=tk.LEFT
        )
        self.url.set(self.options.url)

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

        # save format for current url domain
        ttk.Button(
            toolbar,
            width=3,
            text='db', command=self.save_format
        ).pack(
            side=tk.LEFT
        )        
        
        # status bar
        self.status = ttk.Label(toolbar, text='')
        self.status.pack(side=tk.LEFT, fill=tk.X)

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
                self.gal.append(image)
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
                self.service.url = future
        return True

    def save_format(self) :
        dom = GrabService.domain(self.url.get())
        self.formats[dom] = self.format.get()
        conf.add_json('formats', self.formats)

    def build_url(self, source) :
        data = [ source, self.service.base ]
        data.extend(source.replace('.','/').split('/'))
        built_url = self.format.get().format(*data)
        logging.info(
            'built_url: {}'.format(
                built_url
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
        for image in self.gal.find_withid(event.state) :
            self.youtube.url = self.build_url(image.source)
            title, video_url = self.youtube.video(720)
            video = Video(video_url, title)
            video.player = 'ffplay'
            proc = video.play()
            logging.info(
                '{} {} {}'.format(
                    proc.pid,
                    video.player.__class__.__name__,
                    self.youtube.url
                )
            )

    def right_click_thumb(self, event=None) :
        for image in self.gal.find_withid(event.state) :
            self.youtube.url = self.build_url(image.source)
            title, video_url = self.youtube.video(720)
            video = Video(video_url, title)
            proc = video.play()
            logging.info(
                '{} {} {}'.format(
                    proc.pid,
                    video.player.__class__.__name__,
                    self.youtube.url
                )
            )

# ------------------------------------------------------------------------------

def parse_args() :
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser_group = parser.add_mutually_exclusive_group(required=False)
    parser.add_argument(
        'url',
        nargs='?',
        default='https://www.youtube.com/feed/trending',
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
    parser.add_argument(
        '-X', '--ext',
        action='append',
        default=[],
        help='filename extension filter (can be repeated)'
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
    if len(args.ext) == 0 :
        args.ext = ['jpg', 'jpeg']

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
    app.geometry('-20+20')
    app.mainloop()

# ------------------------------------------------------------------------------

if __name__ == '__main__' :
    main()
