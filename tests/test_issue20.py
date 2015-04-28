# -*- coding: utf-8 -*-
"""\
Tests against <https://github.com/mnooner256/pyqrcode/issues/20>
"""
from __future__ import unicode_literals
from nose.tools import ok_
import pyqrcode


class KeepTrackOfClose():

    def __init__(self):
        self.is_closed = False

    def write(self, x):
        pass

    def close(self):
        self.is_closed = True


def test_donot_close_png():
    code = pyqrcode.create('a')
    out = KeepTrackOfClose()
    code.png(out)
    ok_(not out.is_closed)


def test_donot_close_svg():
    code = pyqrcode.create('a')
    out = KeepTrackOfClose()
    code.svg(out)
    ok_(not out.is_closed)


if __name__ == '__main__':
    import nose
    nose.core.runmodule()
