# -*- encoding: utf-8 -*-
from __future__ import (
    absolute_import,
    print_function, division,
    unicode_literals
)

import logging
logging.basicConfig(level=logging.DEBUG)

try :
    import context
except ImportError :
    from . import context

try :
    import tkinter as tk
    import tkinter.ttk as ttk
except ImportError :
    import Tkinter as tk
    import ttk

import core.elements
import widgets.images

i = core.elements.Image('C:/Users/Public/Pictures/Sample Pictures/Lighthouse.jpg')
j = core.elements.Image('https://dummyimage.com/640x480')

root = tk.Tk()

label1 = widgets.images.ImageLabel(root, image=i)
label1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

label2 = widgets.images.ImageLabel(root)
label2.image = j
label2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

root.mainloop()
    
