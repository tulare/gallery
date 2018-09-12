# -*- encoding: utf-8 -*-
from __future__ import (
    absolute_import,
    print_function, division,
    unicode_literals
)

# logging
import logging
log = logging.getLogger(__name__)
log.debug('MODULE {}'.format(__name__))

import os
import re
import copy
import abc

import PIL.Image, PIL.ImageTk, PIL.ImageDraw, PIL.ImageFont
from io import BytesIO

from pk.services.exceptions import ServiceError
from pk.services.web import WebRequest
from helpers.observer import Observable

# --------------------------------------------------------------------

class ImageBase(Observable) :
    
    def __init__(self) :
        super(ImageBase, self).__init__()
        self.props = {}
        self.debug('__INIT__')

    def __getitem__(self, key) :
        return self.props[key]

    def __setitem__(self, key, value) :
        self.props[key] = value
        
    @abc.abstractproperty
    def source(self) :
        pass
    
    @abc.abstractproperty
    def photo(self) :
        pass

    @abc.abstractproperty
    def photo_thumb(self) :
        pass

    def debug(self, label, **fields) :
        log.debug(
            '{} {} #SELF {}'.format(
                label,
                self.__class__.__name__,
                self
            )
        )
        for key, value in fields.items():
            log.debug(
                '{} {} #{} {}'.format(
                    label,
                    self.__class__.__name__,
                    key.upper(),
                    value
                )
            )

# --------------------------------------------------------------------

class Image(ImageBase) :

    webRequest = WebRequest()                    

    def __init__(self, source=None, thumbsize=(192, 192)) :
        super(Image, self).__init__()

        self._vars()

        self.thumbsize = thumbsize
        self.source = source

    def __del__(self) :
        self.debug('__DEL__')
        # notification de suppression
        self.notify(image=None)

    def _vars(self) :
        self._source = None
        self._image = None
        self._photo = None
        self._thumb = None
        self._photo_thumb = None
                
    @property
    def source(self) :
        return self._source

    @source.setter
    def source(self, src) :
        self.debug('@SOURCE.SETTER', source=src)
        self._vars()
        self._source = src
        self._load()
        self.notify(image=self, source=src)

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
            self.debug('@PHOTO', image=self._image, photo=self._photo)
        return self._photo

    @property
    def thumb(self) :
        if self._thumb is None :
            self._thumb = self.image.copy()
            self._thumb.thumbnail(self.thumbsize)
            self.debug('@THUMB', image=self._image, thumb=self._thumb)
        return self._thumb

    @property
    def photo_thumb(self) :
        if self._photo_thumb is None :
            self._photo_thumb = PIL.ImageTk.PhotoImage(self.thumb)
            self.debug('@PHOTO_THUMB', thumb=self._thumb, photo_thumb=self._photo_thumb)
        return self._photo_thumb
        
    def getbuffer(self, new_format=None) :
        bytesIO = BytesIO()
        self.image.save(bytesIO, new_format or self.image.format)
        return bytesIO.getbuffer()

    def _load(self) :

        if self.source is None :
            self.debug('NONE_SOURCE')
            self._image = self._error('No image')
            return
        
        if isinstance(self.source, Image) :
            self._image = copy.deepcopy(self.source.image)
            #self._image = self.source.image.copy()
            self._source = self.source.source
            self.debug('IMAGE_SOURCE', source=self.source, image=self.image)
            return

        if isinstance(self.source, PIL.Image.Image) :
            self._image = copy.deepcopy(self.source)
            #self._image = self.source.copy()
            self.debug('PIL_IMAGE_SOURCE', source=self.source, image=self.image)
            return

        if isinstance(self.source, memoryview) :
            self._image = PIL.Image.open(BytesIO(self.source))
            self.debug('MEMORYVIEW_SOURCE', source=self.source, image=self.image)
            return

        if isinstance(self.source, ''.__class__) :
            if re.match('http.*://', self.source) :
                try :
                    #image_bytes = self.webRequest(self.source).content
                    image_web = self.webRequest(self.source)
                    image_bytes = self.webRequest(self.source).read()
                    self._image = PIL.Image.open(BytesIO(image_bytes))
                except (ServiceError, OSError) as e :
                    self._image = self._error(repr(e))
                    log.error(
                        '{}#{} {}'.format(
                            self.__class__.__name__,
                            self,
                            repr(e)
                        )
                    )                    
                self.debug('URL_SOURCE', source=self.source, image=self.image)
            else :
                self._image = PIL.Image.open(self.source)
                self.debug('FILE_SOURCE', source=self.source, image=self.image)

            return

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

# --------------------------------------------------------------------

class ImageNone(Image) :

    def __init__(self) :
        super(ImageNone, self).__init__(
            source='https://dummyimage.com/192x144/ff0000/ffffff?text=no+image'
        )

# --------------------------------------------------------------------
