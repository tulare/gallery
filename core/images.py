# -*- encoding: utf-8 -*-

import re
import PIL.Image, PIL.ImageTk
from io import BytesIO

from helpers.delegation import delegate_as
from helpers.services import WebRequest

@delegate_as(PIL.Image.Image, to='image', include={'size'})
class Image :

    webRequest = WebRequest()

    def __init__(self, source=None, thumbsize=(192,192)) :
        self.thumbsize = thumbsize
        self._load_source(source)

    def _load_source(self, source) :
        self._source = source
        self.image = None
        self._thumbnail = None
        self._photo = None

        if isinstance(source, PIL.Image.Image) :
            self.image = source.copy()

        if isinstance(source, memoryview) :
            self.image = PIL.Image.open(BytesIO(source))

        if isinstance(source, str) :
            if re.match('http.*://', source) :
                image_bytes = self.webRequest(source).content
                self.image = PIL.Image.open(BytesIO(image_bytes))
            else :
                self.image = PIL.Image.open(source)

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

