# -*- encoding: utf-8 -*-

import unittest

import logging
import tkinter as tk
import tkinter.ttk as ttk

import core.elements
import widgets.images

from . import locator

# ---

class Test_00_elements(unittest.TestCase) :

    def setUp(self) :
        self.i = core.elements.Image(f'{locator.location}/samples/640x480.jpg')
        self.j = core.elements.Image('https://dummyimage.com/640x480/fff/00f')

    def tearDown(self):
        self.i.image.close()
        self.j.image.close()
    
    def test_00_Trivial(self) :
        assert True, 'True basic trivial test'

    def test_01_Widgets(self) :
        assert show_widgets(self.i, self.j), 'show widgets'
        #assert True, 'Widgets'

# ---

def show_widgets(i, j) :

    root = tk.Tk()
    label1 = widgets.images.ImageLabel(root, image=i)
    label1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    label2 = widgets.images.ImageLabel(root)
    label2.image = j
    label2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    root.after(2500, root.destroy)
    
    root.mainloop()
    
    return True

# ---

if __name__ == '__main__' :
    unittest.main()
    
