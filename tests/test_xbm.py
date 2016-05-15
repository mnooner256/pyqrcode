# -*- coding: utf-8 -*-
"""\
XBM related tests.
"""
from __future__ import unicode_literals, absolute_import
from nose.tools import eq_, raises
import nose
import os
import pyqrcode

#Create by:
#   First I ran: pyqrcode.create('Test', scale=1).png('test.png')
#   Next, I used GIMP to convert it to a XBM file.
expected = '''#define im_width 29
#define im_height 29
static unsigned char im_bits[] = {
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0xf0, 0x17, 0xfd, 0x01, 0x10, 0xe4, 0x05, 0x01,
   0xd0, 0xb5, 0x75, 0x01, 0xd0, 0xc5, 0x74, 0x01, 0xd0, 0xb5, 0x74, 0x01,
   0x10, 0x24, 0x05, 0x01, 0xf0, 0x57, 0xfd, 0x01, 0x00, 0x70, 0x01, 0x00,
   0x00, 0x06, 0x55, 0x01, 0xf0, 0xf0, 0x76, 0x00, 0xc0, 0xb5, 0xf3, 0x00,
   0x80, 0x82, 0x70, 0x00, 0x40, 0xd4, 0x06, 0x01, 0x00, 0x50, 0xcc, 0x00,
   0xf0, 0x47, 0xac, 0x00, 0x10, 0xb4, 0x7b, 0x01, 0xd0, 0x45, 0xaa, 0x00,
   0xd0, 0xe5, 0x66, 0x00, 0xd0, 0x25, 0xe3, 0x01, 0x10, 0x64, 0x57, 0x00,
   0xf0, 0xa7, 0xd5, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };'''
   
def decompose_xbm(s):
    import re
    
    width = re.search('width ([0-9]+)', s).group(1)
    height = re.search('height ([0-9]+)', s).group(1)
    bits = re.findall(r'(0x[0-9][0-9])', s)
    
    return width, height, bits

def test_xbm():
    """Test the xbm render against a known good.
    
    This test checks the *values* contained in the XBM, not the text.
    """
    c = pyqrcode.create('Test').xbm(scale=1)
    
    #Testing number-by-number to get more useful failure message
    c_width, c_height, c_bits = decompose_xbm(c)
    e_width, e_height, e_bits = decompose_xbm(expected)
    
    #Check the there is the same width and height
    eq_(c_width, e_width)
    eq_(c_height, e_height)
    
    #Check that there is the same number of bits
    eq_(len(c_bits), len(e_bits))
    
    #Check the bit values
    for i in range(len(e_bits)):
        eq_(c_bits[i], e_bits[i],
            "Wrong value at {0}: {1} != {2}".format(i, c_bits[i], e_bits[i]))
        
def test_xbm_with_tkinter():
    """Test XBM renderer is compatible with Tkinter
    """
    #Under TOX tkinter testing does not work, skip if tox environemnt
    if not os.getenv('DISPLAY'):
        raise nose.SkipTest()
    
    #Python 2 vs 3
    try:
        import Tkinter as tkinter
    except:
        import tkinter

    code = pyqrcode.create('Test')
    code_size = code.get_png_size(scale=1)
    code_xbm = code.xbm(scale=1)
    
    top = tkinter.Tk()
    bitmap = tkinter.BitmapImage(data=code_xbm)

    eq_(bitmap.width(), code_size)
    eq_(bitmap.height(), code_size)

if __name__ == '__main__':
    import nose
    nose.core.runmodule()
