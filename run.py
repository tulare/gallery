#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os, subprocess
import argparse
import functools
import tempfile
import tkinter as tk

from core.images import Image
from helpers.services import GrabService, ServiceError
from widgets.gallery import GalleryFrame

def clear() :
    status.config(text='')
    gal.clear()

def load() :
    clear()
    if args.images :
        status.config(text='work in progress...')
        for image in gs.images :
            gal.append(image)
        status.config(text='images done.')
    if args.links :
        status.config(text='work in progress...')
        for link in gs.links :
            gal.append(link)
        status.config(text='links done.')

def update() :
    status.config(text='work in progress...')
    gs.update()
    status.config(text='update done.')
    load()

def reload() :
    status.config(text='work in progress...')
    gal.reload()
    status.config(text='reload done.')

def reorg(cols) :
    gal.cols = cols

def click_thumb(event=None) :
    global tmpdir, tmpidx

    for image in event.widget.master.current :
        image_path = '{}{}{}_{:03d}.jpg'.format(
            tmpdir.name, os.path.sep, 'out', tmpidx
        )
        tmpidx += 1
        image.save(image_path)
        os.system('PhotoViewer ' + image_path) 
##            subprocess.run([
##                'rundll32.exe',
##                'C:/Program Files/Windows Photo Viewer/PhotoViewer.dll',
##                ',',
##                'ImageView_Fullscreen',
##                image_path
##            ])

UA = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0"
Image.webRequest.user_agent = UA

# Gestion paramètres ligne de commande
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser_group = parser.add_mutually_exclusive_group(required=True)
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
args = parser.parse_args()
print(args)

# Grab Service
gs = GrabService()
gs.user_agent = UA
try :
    gs.url = args.url
except ServiceError as e :
    print(e)
    exit()

# Temporary directory
tmpdir = tempfile.TemporaryDirectory()
tmpidx = 1

# User Interface
root = tk.Tk()
toolbar = tk.Frame(root)
toolbar.pack(fill=tk.X)
tk.Button(toolbar, text='clear', command=clear).pack(side=tk.LEFT)
tk.Button(toolbar, text='load', command=load).pack(side=tk.LEFT)
tk.Button(toolbar, text='update + load', command=update).pack(side=tk.LEFT)
tk.Button(toolbar, text='reload', command=reload).pack(side=tk.LEFT)
tk.Button(toolbar, text='reorg by 7', command=functools.partial(reorg, cols=8)).pack(side=tk.LEFT)
tk.Button(toolbar, text='reorg by 10', command=functools.partial(reorg, cols=10)).pack(side=tk.LEFT)
status = tk.Label(toolbar, text='')
status.pack(side=tk.LEFT, fill=tk.X)
gal = GalleryFrame(root, width=1400, height=800 ,bg='darkseagreen')
gal.pack(fill=tk.BOTH, expand=True)
gal.cols = 7

# Action on thumbnail click
root.bind('<<ClickThumb>>', click_thumb)

# Application main loop
root.mainloop()
