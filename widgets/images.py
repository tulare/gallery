# -*- encoding: utf-8 -*-
from __future__ import (
    absolute_import,
    print_function, division,
    unicode_literals,
)

# logging
import logging
log = logging.getLogger(__name__)
log.debug('MODULE {}'.format(__name__))

##try :
##    import __locator__
##except ImportError :
##    pass

import weakref

try : # python 3.x
    import tkinter as tk
    import tkinter.ttk as ttk
except ImportError : # python 2.x
    import Tkinter as tk
    import ttk
    
import core.elements
from helpers.observer import IObserver

# -------------------------------------------------------------------------

class ImageLabel(ttk.Label, IObserver) :

    imageNone = core.elements.ImageNone()

    def __init__(self, master=None,
                 image=None, thumb=False, **kwargs) :
        super(ImageLabel, self).__init__(master, **kwargs)
        self.debug('__INIT__', image=image, thumb=thumb)
        self._thumb = thumb
        self.image = image
        
    def winfo_exists(self) :
        try :
            return tk.getboolean( super(ImageLabel, self).winfo_exists() )
        except tk.TclError as e :
            self.debug('WINFO_EXISTS', message=e)
            return False
            
    @property
    def image(self) :
        return self._image()

    @property
    def thumb(self) :
        return self._thumb

    @thumb.setter
    def thumb(self, value) :
        self._thumb = value
        self._update()

    @image.setter
    def image(self, image) :
        alive = self.winfo_exists()
        self.debug('@IMAGE.SETTER', image=image, alive=alive)

        if image is None :
            self._image = weakref.ref(self.imageNone)
        else :
            self._image = weakref.ref(image)

        if self.image is not None and alive :
            self.image.addObserver(self)
            self._update()

    def _update(self) :
        if self.thumb :
            self['image'] = self.image.photo_thumb
        else :
            self['image'] = self.image.photo
    
    def observe(self, *args, **kwargs) :
        alive = self.winfo_exists()
        self.debug('OBSERVE', args=args, kwargs=kwargs, alive=alive)
        if 'image' in kwargs and alive :
            self.image = kwargs['image']

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

# -------------------------------------------------------------------------

class ImageCanvas(IObserver) :

    imageNone = core.elements.ImageNone()

    def __init__(self, canvas, image, x, y, tag) :
        super(ImageCanvas, self).__init__()
        self.debug('__INIT__', canvas=canvas, image=image, x=x, y=y, tag=tag)
        self._image = None
        self.id = None
        
        self.canvas, self.x, self.y, self.tag = canvas, x, y, tag
        self.image = image

    def canvas_alive(self) :
        try :
            return tk.getboolean( self.canvas.winfo_exists() )
        except tk.TclError as e :
            self.debug('CANVAS_ALIVE', message=e)
            return False

    @property
    def image(self) :
        return self._image()

    @image.setter
    def image(self, image) :
        alive = self.canvas_alive()
        if image is None :
            self._image = weakref.ref(self.imageNone)
        else :
            self._image = weakref.ref(image)
        

        if self.image is not None and alive :
            self.image.addObserver(self)
            self._update()

        self.debug('@IMAGE.SETTER', id=self.id, new=image, old=self.image, alive=alive)

    def _update(self) :
        if self.id is None :
            self.id = self.canvas.create_image(
                self.x, self.y,
                anchor=tk.CENTER,
                image=self.image.photo_thumb,
                tag = self.tag
            )
        else :
            self.canvas.itemconfig(
                self.id,
                image=self.image.photo_thumb
            )
        self.image['id'] = self.id
        
    def observe(self, *args, **kwargs) :
        alive = self.canvas_alive()
        self.debug('OBSERVE', args=args, kwargs=kwargs, alive=alive)
        if 'image' in kwargs and alive :
            self.image = kwargs['image']
            
    def __del__(self) :
        self.debug('__DEL__')

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

if __name__ == '__main__' :
    logging.basicConfig(level=logging.DEBUG)

    im = core.elements.Image('https://dummyimage.com/320x200')

    root = tk.Tk()
    root.geometry('-200+20')

    label = ImageLabel(root)
    label.pack(fill=tk.BOTH, expand=True)
    label.image = im

    canvas = tk.Canvas(width=320, height=400)
    canvas.pack(fill=tk.BOTH, expand=True)
    ImageCanvas(canvas, image=im, x=160, y=100, tag='thumbnail')
    ImageCanvas(canvas, image=im, x=160, y=300, tag='thumbnail')

    logging.info('************* MAIN_LOOP ***************')

    root.mainloop()
    
