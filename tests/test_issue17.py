# -*- coding: utf-8 -*-
"""\
Tests against <https://github.com/mnooner256/pyqrcode/issues/17>
"""
from __future__ import unicode_literals
from nose.tools import eq_
import pyqrcode


def test_umlaut():
    s = 'Märchenbuch'
    code = pyqrcode.create(s, error='M')
    eq_('binary', code.mode)
    eq_(s, code.data)


def test_umlaut_utf8():
    s = 'Märchenbuch'
    code = pyqrcode.create(s, error='M', encoding='utf-8')
    eq_('binary', code.mode)
    eq_(s, code.data)


def test_ascii():
    s = 'MAERCHENBUCH'
    code = pyqrcode.create(s, error='M', encoding='utf-8')
    eq_('alphanumeric', code.mode)
    eq_(s, code.data)


def test_ascii2():
    s = 'MAERCHENBUCH'
    code = pyqrcode.create(s, error='M', encoding=None)
    eq_('alphanumeric', code.mode)
    eq_(s, code.data)


if __name__ == '__main__':
    import nose
    nose.core.runmodule()
