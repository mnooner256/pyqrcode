# -*- coding: utf-8 -*-
"""\
Tests against <https://github.com/mnooner256/pyqrcode/issues/34>
"""
from __future__ import unicode_literals
from nose.tools import eq_
import pyqrcode


def test_default_encoding():
    qr = pyqrcode.create('Märchenbücher', error='m')
    # 1 since the data fits into version 1 if ISO/IEC 8859-1 (the default
    # encoding) is used
    eq_(1, qr.version)
    eq_('binary', qr.mode)


def test_encoding_latin1():
    qr = pyqrcode.create('Märchenbücher', error='m', encoding='latin1')
    eq_(1, qr.version)
    eq_('binary', qr.mode)


def test_encoding_utf8():
    qr = pyqrcode.create('Märchenbücher', error='m', encoding='utf-8')
    eq_(2, qr.version)
    eq_('binary', qr.mode)


if __name__ == '__main__':
    import nose
    nose.core.runmodule()
