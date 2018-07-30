# -*- encoding: utf-8 -*-

# logging
import logging
log = logging.getLogger(__name__)
log.debug('MODULE {}'.format(__name__))

try :
    import __locator__
except ImportError :
    pass

import weakref
import tkinter as tk
import tkinter.ttk as ttk

import core.elements


class CanvasImage :

    def __init__(self, canvas, image, x, y, tag) :
        self._image = None
        self.id = None
        
        self.canvas, self.x, self.y, self.tag = canvas, x, y, tag
        self.image = image

    @property
    def image(self) :
        return self._image

    @image.setter
    def image(self, image) :
        log.debug(
            '{} @IMAGE ID {} NEW {} OLD {}'.format(
                self.__class__.__name__,
                self.id,
                image,
                self.image
            )
        )
        self._image = image

        self.photo_thumb_ref = weakref.ref(
            self.image.photo_thumbnail,
            self.repairPhoto
        )

        if self.id is None :
            self.id = self.canvas.create_image(
                self.x, self.y,
                anchor=tk.CENTER,
                image=self.photo_thumb_ref(),
                tag = self.tag
            )
        else :
            self.canvas.itemconfig(
                self.id,
                image=self.photo_thumb_ref()
            )
        self.image['id'] = self.id
        self.image['ref'] = self

    def repairPhoto(self, reference) :
        log.debug('{} repair REF {} IMAGE {}'.format(
            self.__class__.__name__,
            reference,
            self.image
            )
        )        
        self.photo_thumb_ref = weakref.ref(
            self.image.photo_thumbnail,
            self.repairPhoto
        )
        self.canvas.itemconfig(
            self.id,
            image=self.photo_thumb_ref()
        )
        
    def __del__(self) :
        log.debug(
            '{} __DEL__ {}'.format(
                self.__class__.__name__,
                self
            )
        )
        
class GalleryFrame(ttk.Frame) :

    def __init__(self, master=None, thumbsize=(192,192), rows=3, cols=5, **kwargs) :
        super().__init__(master, **kwargs)

        self.images = []
        self._cols = cols
        self.thumbsize = thumbsize
        self.slotsize = (self.thumbsize[0] + 8, self.thumbsize[1] + 32)

        self.h = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.v = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.canvas = tk.Canvas(
            self,
            scrollregion=self.scrollregion,
            yscrollcommand=self.v.set,
            xscrollcommand=self.h.set,
            width=self.slotsize[0] * self._cols,
            height=self.slotsize[1] * rows
        )

        self.h.config(command=self.canvas.xview)
        self.v.config(command=self.canvas.yview)

        self.h.pack(side=tk.BOTTOM, fill=tk.X)
        self.v.pack(side=tk.RIGHT, fill=tk.Y)        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)        

        self.canvas.tag_bind('thumbnail', '<Button-1>', self._click_event)
        self.canvas.tag_bind('thumbnail', '<Button-3>', self._right_click_event)
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
        return self.canvas.find_withtag('current')


    def find_withid(self, canvas_id) :
        return filter(
            lambda i : i['id'] == canvas_id,
            self.images
        )

    def append(self, source, title=None) :
        image = core.elements.Image(source, self.thumbsize)
        log.debug(
            '{} append IMAGE "{}" {}'.format(
                self.__class__.__name__,
                image.basename,
                image.image,
            )
        )
        self._add_entry(image)

    def replace(self, indice, source) :
        if indice < self.entries :
            self.images[indice].source = source

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
                self.update()
        elif indice < self.entries :
            image = self.images[indice]
            image.source = image.source

    def reorg(self) :
        saved_images = self.images.copy()
        self.clear()

        for image in saved_images :
            self._add_entry(image)

    def _add_entry(self, image) :
        CanvasImage(
            self.canvas,
            image,
            self.posx, self.posy,
            tag='thumbnail',
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
        self.canvas.event_generate(
            '<<ClickThumb>>',
            x=event.x, y=event.y,
            state=self.current[0]
        )

    def _right_click_event(self, event) :
        self.canvas.event_generate(
            '<<RightClickThumb>>',
            x=event.x, y=event.y,
            state=self.current[0]
        )

    def _mouse_wheel_event(self, event) :
        if event.num == 5 or event.delta == -120 :
            self.canvas.yview('scroll', 1, 'units')
        if event.num == 4 or event.delta == 120 :
            self.canvas.yview('scroll', -1, 'units')

if __name__ == '__main__' :
    logging.basicConfig(level=logging.DEBUG)
    
    root = tk.Tk()

    gal = GalleryFrame(root, rows=3, cols=3)
    gal.pack(fill=tk.BOTH, expand=True)
    gal.append(None)
    gal.append('C:/Users/Public/Pictures/Sample Pictures/Tulips.jpg')
    gal.append('http://httpbin.org/image/jpeg')
    gal.append('https://dummyimage.com/1024x768')
    gal.append('https://dummyimage.com/800x600')

    #root.mainloop()
