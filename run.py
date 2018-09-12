# -*- encoding: utf-8 -*-
from __future__ import (
    absolute_import,
    print_function, division,
    unicode_literals
)

# Configuration
import requirements
from pk.config import Configuration
conf = Configuration()
assert conf.checklist(['User-Agent'])

# Paramètres ligne de commande
import logging
import argparse

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
    default=[]
)
parser.add_argument(
    '-F', '--format',
    default='{7}',
    help='format'
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

# Logging
logging.basicConfig(level=args.loglevel)
logging.info('start logging')

try : # python 3.x
    import tkinter as tk
    import tkinter.ttk as ttk
except : # python 2.x
    import Tkinter as tk
    import ttk
    
import functools
import tempfile
import subprocess

# Services
from pk.services.exceptions import ServiceError
from pk.services.web import GrabService
from pk.services.youtube import YoutubeService

# Widgets
import core.elements
core.elements.Image.webRequest.user_agent = conf.get('User-Agent')
from widgets.gallery import GalleryFrame
from widgets.window import ImageWindow

# Helpers
from helpers.video import Video


class Application(tk.Tk, object) :

    def __init__(self, options, service) :
        super(Application, self).__init__()
        self.options = options
        self.service = service
        self.youtube = YoutubeService()
        self.createWidgets()

    def createWidgets(self) :
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X)
        ttk.Button(
            toolbar,
            text='clear', command=self.clear
        ).pack(
            side=tk.LEFT
        )
        ttk.Button(
            toolbar,
            text='load', command=self.load
        ).pack(
            side=tk.LEFT
        )
        ttk.Button(
            toolbar,
            text='update + load', command=self.update
        ).pack(
            side=tk.LEFT
        )
        ttk.Button(
            toolbar,
            text='refresh', command=self.reload
        ).pack(
            side=tk.LEFT
        )

        self.cols = tk.IntVar()
        spinBox = tk.Spinbox(
            toolbar,
            from_=3, to=8,
            textvariable=self.cols, command=self.reorg)
        spinBox.pack(side=tk.LEFT)
        self.cols.set(5)

        self.url = tk.StringVar()
        ttk.Entry(
            toolbar,
            width=50,
            textvariable=self.url
        ).pack(
            side=tk.LEFT
        )
        self.url.set(self.service.url)

        self.format = tk.StringVar()
        ttk.Entry(
            toolbar,
            width=20,
            textvariable=self.format
        ).pack(
            side=tk.LEFT
        )
        self.format.set(self.options.format)
        
        self.status = ttk.Label(toolbar, text='')
        self.status.pack(side=tk.LEFT, fill=tk.X)

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
        logging.info('clear')
        self.status.config(text='')
        self.gal.clear()

    def load(self) :
        logging.info('load in progress')
        self.clear()
        if self.options.images :
            logging.info('load images in progress')
            self.status.config(text='work in progress...')
            for image in self.service.images :
                self.gal.append(image)
            logging.info('load images done')
            self.status.config(text='images done.')
        if self.options.links :
            logging.info('load links in progress')
            self.status.config(text='work in progress...')
            for link in self.service.links :
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

    def build_url(self, source) :
        data = [ self.service.base ]
        data.extend(source.replace('.','/').split('/'))
        built_url = self.format.get().format(*data)
        logging.warning(
            'built_url: {}'.format(
                built_url
            )
        )
        return built_url

    def middle_click_thumb(self, event=None) :
        for image in self.gal.find_withid(event.state) :
            self.youtube.url = self.build_url(image.source)
            title, video_url = self.youtube.video(720)
            video = Video(video_url, title)
            video.player = 'ffplay'
            proc = video.play()
            logging.warning(
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
            logging.warning(
                '{} {} {}'.format(
                    proc.pid,
                    video.player.__class__.__name__,
                    self.youtube.url
                )
            )

if __name__ == '__main__' :

    logging.info('args=%r', args)

    # Grab Service
    logging.info('starting grab service')
    gs = GrabService()
    gs.user_agent = conf.get('User-Agent')
    gs.ext = args.ext
    try :
        gs.url = args.url
    except ServiceError as e :
        logging.error(e)
        exit()

    # User Interface and mainloop
    app = Application(options=args, service=gs)
    app.geometry('-20+20')
    app.mainloop()
