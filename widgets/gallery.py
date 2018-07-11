# -*- encoding: utf-8 -*-

import tkinter as tk
from core.images import Image

class GalleryFrame(tk.Frame) :

    def __init__(self, master=None, **kwargs) :
        super().__init__(master, **kwargs)

        self.images = []
        self._cols = 5
        self.thumbsize = (192, 192)
        self.slotsize = (self.thumbsize[0] + 8, self.thumbsize[1] + 32)

        self.h = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.v = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.canvas = tk.Canvas(
            self,
            scrollregion=self.scrollregion,
            yscrollcommand=self.v.set,
            xscrollcommand=self.h.set,
            **kwargs
        )

        self.h.config(command=self.canvas.xview)
        self.v.config(command=self.canvas.yview)

        self.h.pack(side=tk.BOTTOM, fill=tk.X)
        self.v.pack(side=tk.RIGHT, fill=tk.Y)        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)        

        self.canvas.tag_bind('thumbnail', '<Button-1>', self._click_event)
        self.canvas.bind('<MouseWheel>', self._mouse_wheel_event)
        self.canvas.bind('<Button-4>', self._mouse_wheel_event)
        self.canvas.bind('<Button-5>', self._mouse_wheel_event)

    @property
    def entries(self) :
        return len(self.images)

    @property
    def cols(self) :
        return self._cols

    @cols.setter
    def cols(self, cols) :
        if cols > 0 :
            self._cols = cols
            self.reorg()

    @property
    def rows(self) :
        return self.entries // self.cols + 1

    @property
    def scrollregion(self) :
        return (0, 0, self.cols * self.slotsize[0], self.rows * self.slotsize[1])

    @property
    def posx(self) :
        return self.entries % self.cols * self.slotsize[0] + self.slotsize[0] // 2

    @property
    def posy(self) :
        return (self.rows - 1) * self.slotsize[1] + self.slotsize[1] // 2

    @property
    def text_posx(self) :
        return self.posx

    @property
    def text_posy(self) :
        return self.posy + self.slotsize[1] // 2.19

    @property
    def current(self) :
        id_list = self.canvas.find_withtag('current')
        return filter(
            lambda i : i.id in id_list,
            self.images
        )

    def append(self, source) :
        image = Image(source)
        self._add_entry(image)

    def replace(self, indice, source) :
        if indice < self.entries :
            image = self.images[indice]
            image.source = source
            self.reload(indice)

    def clear(self) :
        self.canvas.delete('all')
        self.images.clear()

    def pop(self, indice=None) :
        if indice is None :
            image = self.images.pop()
        elif indice < self.entries :
            image = self.images.pop(indice)
        else :
            return
        self.reorg()
        return image            
        
    def reload(self, indice=None) :
        if indice is None :            
            for image in self.images :
                image.source = image.source
                self.canvas.itemconfig(image.id, image=image.thumbnail)
                self.update()
        elif indice < self.entries :
            image = self.images[indice]
            self.canvas.itemconfig(image.id, image=image.thumbnail)

    def reorg(self) :
        saved_images = self.images.copy()
        self.clear()

        for image in saved_images :
            self._add_entry(image)

    def _add_entry(self, image) :
        image.id = self.canvas.create_image(
            self.posx, self.posy,
            anchor=tk.CENTER,
            image=image.thumbnail,
            tag = 'thumbnail'
        )
        self.canvas.create_text(
            self.text_posx + 1, self.text_posy + 1,
            anchor=tk.CENTER,
            width=self.slotsize[0],
            text=image.basename,
            tag='shadow',
            fill='black'
        )
        self.canvas.create_text(
            self.text_posx, self.text_posy,
            anchor=tk.CENTER,
            width=self.slotsize[0],
            text=image.basename,
            tag='text',
            fill='royalblue'
        )
        self.canvas.config(scrollregion=self.scrollregion)
        self.images.append(image)
        self.update()

    def _click_event(self, event) :
        self.canvas.event_generate('<<ClickThumb>>', x=event.x, y=event.y)

    def _mouse_wheel_event(self, event) :
        if event.num == 5 or event.delta == -120 :
            self.canvas.yview('scroll', 1, 'units')
        if event.num == 4 or event.delta == 120 :
            self.canvas.yview('scroll', -1, 'units')
