# -*- encoding: utf-8 -*-

import os
import re
import PIL.Image, PIL.ImageTk, PIL.ImageDraw, PIL.ImageFont
from io import BytesIO

from helpers.delegation import delegate_as
from helpers.services import WebRequest, ServiceError

@delegate_as(PIL.Image.Image, to='image',
             include={'size', 'info', 'mode'})
class Image :

    webRequest = WebRequest()

    def __init__(self, source=None, thumbsize=(192, 192)) :
        self.thumbsize = thumbsize
        self.props = dict()
        self._load_source(source)

    @property
    def photo(self) :
        if self._photo is None :
            self._photo = PIL.ImageTk.PhotoImage(self.image) 
        return self._photo

    @property
    def thumbnail(self) :
        if self._thumbnail is None :
            thumbnail = self.image.copy()
            thumbnail.thumbnail(self.thumbsize)
            self._thumbnail = PIL.ImageTk.PhotoImage(thumbnail)
        return self._thumbnail
        
    @property
    def source(self) :
        return self._source

    @source.setter
    def source(self, source) :
        self._load_source(source)

    @property
    def id(self) :
        return self.image_id
    
    @id.setter
    def id(self, image_id) :
        self.image_id = image_id

    @property
    def filename(self) :
        return self.image.__dict__.get('filename') or self.source

    @property
    def basename(self) :
        return os.path.basename(
            self.filename.split('?').pop(0)
        )

    def getbuffer(self, format=None) :
        bufIO = BytesIO()
        self.image.save(bufIO, format or self.image.format)
        return bufIO.getbuffer()
        

    def _load_source(self, source) :
        self._source = source
        self.image = None
        self._thumbnail = None
        self._photo = None

        if source is None :
            self.image = self._load_error('No image')

        if isinstance(source, Image) :
            self.image = source.image.copy()
            self.format = source.format
            self.format_description = source.format_description
            self._source = source.source

        if isinstance(source, PIL.Image.Image) :
            self.image = source.copy()
            self.format = source.format
            self.format_description = source.format_description

        if isinstance(source, memoryview) :
            self.image = PIL.Image.open(BytesIO(source))

        if isinstance(source, str) :
            if re.match('http.*://', source) :
                try :
                    image_bytes = self.webRequest(source).content
                    self.image = PIL.Image.open(BytesIO(image_bytes))
                except ServiceError as e :
                    self.image = self._load_error(repr(e))
            else :
                self.image = PIL.Image.open(source)

    def _load_error(self, message) :
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
    i = Image('C:/Users/Public/Pictures/Sample Pictures/Desert.jpg')
    j = Image('https://dummyimage.com/1024x768/888/000')
