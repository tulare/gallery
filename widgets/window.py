# -*- encoding: utf-8 -*-

import tkinter as tk
from core.images import Image

class ImageWindow(tk.Toplevel) :

    placeholder = Image('https://dummyimage.com/1024x768/888/000')
    
    def __init__(self, master=None, source=None, closeFunc=None, **kwargs) :
        super().__init__(master, **kwargs)
        #self.title(title)
        self._init_image(source)
        self.title(self._image.basename)
        self.closeFunc = closeFunc
        self.protocol('WM_DELETE_WINDOW', self._closeWindow)
        self.createWidgets()

    def createWidgets(self) :
        self.labelPhoto = tk.Label(self)
        self.labelPhoto.config(image=self.image.photo)
        self.labelPhoto.pack(fill=tk.BOTH, expand=True)

    @property
    def image(self) :
        return self._image

    @image.setter
    def image(self, source) :
        self._init_image(source)
        self.labelPhoto.config(image=self.image.photo)

    def _init_image(self, source) :
        if source is None :
            self._image = self.placeholder
        else :
            self._image = Image(source)

    def _closeWindow(self) :
        if callable(self.closeFunc) :
            if self.closeFunc(self) is True :
                self.destroy()

if __name__ == '__main__' :
    root = tk.Tk()
    top = ImageWindow(root, source='http://httpbin.org/image/jpeg')
