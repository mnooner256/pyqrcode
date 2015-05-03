# -*- coding: utf-8 -*-
"""\
Tests against <https://github.com/mnooner256/pyqrcode/issues/29>

Negative numbers aren't supported by "numeric" mode.
"""
from __future__ import unicode_literals
from nose.tools import eq_
import pyqrcode


def test_negative_int():
    qr = pyqrcode.create(-7)
    eq_('-7', qr.data)
    eq_('alphanumeric', qr.mode)


def test_negative_int_str():
    qr = pyqrcode.create('-123')
    eq_(b'-123', qr.data)
    eq_('alphanumeric', qr.mode)


if __name__ == '__main__':
    import nose
    nose.core.runmodule()
