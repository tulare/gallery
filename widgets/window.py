# -*- encoding: utf-8 -*-
from __future__ import (
    absolute_import,
    print_function, division
)

# logging
import logging
log = logging.getLogger(__name__)
log.debug('MODULE {}'.format(__name__))

##try :
##    import __locator__
##except ImportError :
##    pass


try : # python 2.x
    import tkinter as tk
    import tkinter.ttk as ttk
except ImportError : # python 3.x
    import Tkinter as tk
    import ttk
    

import core.elements
import widgets.images

# -------------------------------------------------------------------------

class ImageWindow(tk.Toplevel, object) :

    def __init__(self, master=None,
                 source=None, title=None, closeFunc=None, **kwargs) :
        super(ImageWindow, self).__init__(master, **kwargs)
        self.debug('__INIT__', source=source, title=title)
        self._init_image(source)
        self.title(title or self._image.basename)
        self.closeFunc = closeFunc
        self.protocol('WM_DELETE_WINDOW', self._closeWindow)
        self.createWidgets()

    def createWidgets(self) :
        self.labelPhoto = widgets.images.ImageLabel(self, image=self.image)
        self.labelPhoto.pack(fill=tk.BOTH, expand=True)

    def destroy(self) :
        self._image = None
        super(ImageWindow, self).destroy()

    @property
    def image(self) :
        return self._image

    @image.setter
    def image(self, source) :
        self.debug('@IMAGE.SETTER', source=source)
        self._init_image(source)
        self.labelPhoto.image = self.image

    def _init_image(self, source) :
        self._image = core.elements.Image(source)

    def _closeWindow(self) :
        if callable(self.closeFunc) :
            if self.closeFunc(self) is True :
                self.destroy()

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

    log.info('====== CREATION IMAGE 1 ******************************')
    im1 = core.elements.Image('http://httpbin.org/image/jpeg')
    log.info('====== CREATION IMAGE 2 ******************************')
    im2 = core.elements.Image('C:/Users/Public/Pictures/Sample Pictures/Hydrangeas.jpg')

    log.info('====== CREATION ROOT APPLICATION ********************')
    root = tk.Tk()

    log.info('====== CREATION LABEL ROOT **************************')
    lab = widgets.images.ImageLabel(root)
    lab.pack(fill=tk.BOTH, expand=True)
    log.info('====== AFFECTATION IMAGE LABEL ROOT *****************')
    lab.image = im1

    log.info('====== CREATION IMAGE WINDOW ************************')
    top = ImageWindow(
        root,
        source=im1,
        closeFunc=lambda widget : True
    )

    def click(event=None) :
        top.image = 'C:/Users/Public/Pictures/Sample Pictures/Jellyfish.jpg'

    top.bind('<Button-1>', click)

    log.info('====== CREATION ROOT MAINLOOP **********************')
    root.mainloop()
    
