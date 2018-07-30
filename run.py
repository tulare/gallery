#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

# Logging
import logging
logging.basicConfig(level=logging.DEBUG)
logging.info('start logging')

import argparse
import functools
import tempfile

import tkinter as tk
import tkinter.ttk as ttk

import core.elements
from helpers.services import GrabService, ServiceError
from widgets.gallery import GalleryFrame
from widgets.window import ImageWindow

UA = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0"
core.elements.Image.webRequest.user_agent = UA

class Application(tk.Tk) :

    def __init__(self, options, service) :
        super().__init__()
        self.options = options
        self.service = service
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
        self.service.update()
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

    def right_click_thumb(self, event=None) :
        for image in self.gal.find_withid(event.state) :
            image.source = image.source

if __name__ == '__main__' :

    # Gestion paramètres ligne de commande
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser_group = parser.add_mutually_exclusive_group(required=False)
    parser.add_argument(
        'url',
        nargs='?',
        default='https://www.megapixl.com/clipart'
    )
    parser_group.add_argument(
        '-I', '--images',
        action='store_true',
        help='capture embedded images'
    )
    parser_group.add_argument(
        '-L', '--links',
        action='store_true',
        help='capture linked images'
    )
    parser.add_argument(
        '-X', '--ext',
        action='append',
        default=[]
    )
    args = parser.parse_args()
    if not args.links :
        args.images = True
    if len(args.ext) == 0 :
        args.ext = ['jpg', 'jpeg']

    logging.info('args=%r', args)

    # Grab Service
    logging.info('starting grab service')
    gs = GrabService()
    gs.user_agent = UA
    gs.ext = args.ext
    try :
        gs.url = args.url
    except ServiceError as e :
        print(e)
        exit()

    # User Interface and mainloop
    app = Application(options=args, service=gs)
    app.geometry('-20+20')
    app.mainloop()
