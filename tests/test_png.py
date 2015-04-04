# -*- coding: utf-8 -*-
"""\
PNG related tests.
"""
from nose.tools import eq_
import pyqrcode


def test_size():
    code = pyqrcode.create('Hello world')
    qr_size = 25
    border = 0
    eq_(qr_size, code.get_png_size(1, border=border))
    border = 1
    eq_((qr_size + 2 * border) * border, code.get_png_size(1, border=border))
    border = 4  # (default border)
    eq_((qr_size + 2 * border) * 1, code.get_png_size())
    eq_((qr_size + 2 * border) * 1, code.get_png_size(1))
    eq_((qr_size + 2 * border) * 4, code.get_png_size(4))
    border = 0
    eq_((qr_size + 2 * border) * 4, code.get_png_size(4, border=border))


if __name__ == '__main__':
    import nose
    nose.core.runmodule()
