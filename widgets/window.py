# -*- encoding: utf-8 -*-

# logging
import logging
log = logging.getLogger(__name__)
log.debug('MODULE {}'.format(__name__))

try :
    import __locator__
except ImportError :
    pass

import tkinter as tk
import tkinter.ttk as ttk
import weakref

import core.elements

class ImageLabel(ttk.Label) :

    def __init__(self, master=None, image=None, **kwargs) :
        super().__init__(master, **kwargs)
        self._image = None
        self.image = image

    @property
    def image(self) :
        return self._image

    @image.setter
    def image(self, image) :
        log.debug('{} @IMAGE NEW {} OLD {}'.format(
            self.__class__.__name__,
            image,
            self.image
            )
        )
        self._image = image
        if image is not None :
            self.photo_ref = weakref.ref(self.image.photo, self.repairPhoto)
            self['image'] = self.photo_ref()

    def repairPhoto(self, reference) :
        log.debug('{} repair REF {} IMAGE {}'.format(
            self.__class__.__name__,
            reference,
            self.image
            )
        )        
        self.photo_ref = weakref.ref(self.image.photo, self.repairPhoto)
        self['image'] = self.photo_ref()


class ImageWindow(tk.Toplevel) :

    def __init__(self, master=None, source=None, closeFunc=None, **kwargs) :
        super().__init__(master, **kwargs)
        self._init_image(source)
        self.title(self._image.basename)
        self.closeFunc = closeFunc
        self.protocol('WM_DELETE_WINDOW', self._closeWindow)
        self.createWidgets()

    def createWidgets(self) :
        self.labelPhoto = ImageLabel(self, image=self.image)
        self.labelPhoto.pack(expand=True)

    @property
    def image(self) :
        return self._image

    @image.setter
    def image(self, source) :
        self._init_image(source)
        self.labelPhoto.image = self.image

    def _init_image(self, source) :
        self._image = core.elements.Image(source)

    def _closeWindow(self) :
        if callable(self.closeFunc) :
            if self.closeFunc(self) is True :
                self.destroy()

if __name__ == '__main__' :
    logging.basicConfig(level=logging.DEBUG)


    im1 = core.elements.Image('http://httpbin.org/image/jpeg')

    im2 = core.elements.Image(
        'C:/Users/Public/Pictures/Sample Pictures/Hydrangeas.jpg'
    )
    
    root = tk.Tk()
    top = ImageWindow(
        root,
        source=im1,
        closeFunc=lambda widget : True
    )

    def click(event=None) :
        top.image = im2

    top.bind('<Button-1>', click)
    top.after(5000, click)

    root.mainloop()
    
