# -*- coding: utf-8 -*-
"""\
Tests against EPS generation.
"""
from __future__ import absolute_import, unicode_literals
import io
from nose.tools import raises
import pyqrcode


@raises(ValueError)
def test_illegal_color_float():
    color = (.1, 1.1, .1)
    qr = pyqrcode.create('test')
    out = io.StringIO()
    qr.eps(out, module_color=color)


@raises(ValueError)
def test_illegal_color_float2():
    color = (-.1, 1.0, .1)
    qr = pyqrcode.create('test')
    out = io.StringIO()
    qr.eps(out, module_color=color)


@raises(ValueError)
def test_illegal_color_int():
    color = (255, 255, 256)
    qr = pyqrcode.create('test')
    out = io.StringIO()
    qr.eps(out, module_color=color)


@raises(ValueError)
def test_illegal_color_int2():
    color = (-1, 1, 1)
    qr = pyqrcode.create('test')
    out = io.StringIO()
    qr.eps(out, module_color=color)



if __name__ == '__main__':
    import nose
    nose.core.runmodule()
