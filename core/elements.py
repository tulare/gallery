# -*- encoding: utf-8 -*-

# logging
import logging
log = logging.getLogger(__name__)
log.debug('MODULE {}'.format(__name__))

try :
    import __locator__
except ImportError :
    pass

import os
import re
import copy

import PIL.Image, PIL.ImageTk, PIL.ImageDraw, PIL.ImageFont
from io import BytesIO

from helpers.services import WebRequest, ServiceError


class Image :

    webRequest = WebRequest()

    def __init__(self, source=None, thumbsize=(192, 192)) :
        self._source = source
        self.thumbsize = thumbsize

        self.props = {}
        self._image_thumb = None
        self._photo = None
        self._photo_thumb = None
        
        self._load()

    def __getitem__(self, key) :
        return self.props[key]

    def __setitem__(self, key, value) :
        self.props[key] = value

    def __del__(self) :
        log.debug(
            '{} __DEL__ {}'.format(
                self.__class__.__name__,
                self
            )
        )

    @property
    def source(self) :
        return self._source

    @source.setter
    def source(self, source) :
        self._source = source
        self._load()

    @property
    def image(self) :
        return self._image

    @property
    def filename(self) :
        try :
            return self.image.filename or self.source
        except AttributeError :
            return self.source

    @property
    def basename(self) :
        return os.path.basename(
            str(self.filename)
        ).split('?').pop(0)

    @property
    def photo(self) :
        if self._photo is None :
            self._photo = PIL.ImageTk.PhotoImage(self.image)
        else :
            log.debug(
                '{} PHOTO {}'.format(
                    self.__class__.__name__,
                    self._photo
                )
            )
        return self._photo

    @property
    def thumbnail(self) :
        if self._image_thumb is None :
            self._image_thumb = self.image.copy()
            self._image_thumb.thumbnail(self.thumbsize)
            log.debug(
                '{} THUMBNAIL {}'.format(
                    self.__class__.__name__,
                    self._image_thumb
                )
            )
        return self._image_thumb

    @property
    def photo_thumbnail(self) :
        if self._photo_thumb is None :
            self._photo_thumb = PIL.ImageTk.PhotoImage(self.thumbnail)
        return self._photo_thumb
        
    def getbuffer(self, new_format=None) :
        bytesIO = BytesIO()
        self.image.save(bytesIO, new_format or self.image.format)
        return bytesIO.getbuffer()

    def _load(self) :
        self._image = None

        while True :
            if self.source is None :
                log.debug(
                    '{} SOURCE None'.format(
                        self.__class__.__name__
                    )
                )
                self._image = self._error('No image')
                break
            
            if isinstance(self.source, Image) :
                log.debug(
                    '{} SOURCE Image {}'.format(
                        self.__class__.__name__,
                        self.source
                    )
                )
                self._image = copy.deepcopy(self.source.image)
                self._source = self.source.source
                break

            if isinstance(self.source, PIL.Image.Image) :
                log.debug(
                    '{} SOURCE PIL.Image.Image {}'.format(
                        self.__class__.__name__,
                        self.source
                    )
                )
                self._image = copy.deepcopy(self.source)
                break

            if isinstance(self.source, memoryview) :
                log.debug(
                    '{} SOURCE memoryview {}'.format(
                        self.__class__.__name__,
                        self.source
                    )
                )
                self._image = PIL.Image.open(BytesIO(self.source))
                break

            if isinstance(self.source, str) :
                if re.match('http.*://', self.source) :
                    log.debug(
                        '{} SOURCE URL "{}"'.format(
                            self.__class__.__name__,
                            self.source
                        )
                    )
                    try :
                        image_bytes = self.webRequest(self.source).content
                        self._image = PIL.Image.open(BytesIO(image_bytes))
                    except ServiceError as e :
                        self._image = self._error(repr(e))
                else :
                    log.debug(
                        '{} SOURCE FILE "{}"'.format(
                            self.__class__.__name__,
                            self.source
                        )
                    )
                    self._image = PIL.Image.open(self.source)
                break

            break

        self._image_thumb = None
        self._photo = None
        self._photo_thumb = None                
                

    def _error(self, message) :
        image_error = PIL.Image.new('RGB', (1024, 768), color='red')

        try :
            fontError = PIL.ImageFont.truetype('DejaVuSans', 72)
            fontMessage = PIL.ImageFont.truetype('DejaVuSans', 24)    
        except OSError :
            fontError = PIL.ImageFont.load_default()
            fontMessage = PIL.ImageFont.load_default()
        
        draw = PIL.ImageDraw.Draw(image_error)
        sizeError = draw.textsize('Image Error', font=fontError)
        sizeMessage = draw.textsize(message, font=fontMessage) 
        draw.text(
            ( (1024 - sizeError[0]) // 2, (768 - sizeError[1])//3 ),
            'Image Error', fill='white', font=fontError
        )
        draw.text(
            ( (1024 - sizeMessage[0]) // 2, (768 - sizeMessage[1]) // 2 ),
            message, fill='yellow', font=fontMessage
        )

        bIO = BytesIO()
        image_error.save(bIO, 'PNG')

        return PIL.Image.open(bIO)

        
if __name__ == '__main__' :
    logging.basicConfig(level=logging.DEBUG)

    import tkinter as tk
    import tkinter.ttk as ttk
    import core.elements
    from widgets.window import ImageLabel

    i = core.elements.Image('C:/Users/Public/Pictures/Sample Pictures/Lighthouse.jpg')
    j = core.elements.Image('https://dummyimage.com/640x480')

    root = tk.Tk()

    label1 = ImageLabel(root, image=i)
    label1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    label2 = ImageLabel(root)
    label2.image = j
    label2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    
    root.mainloop()
    
    
