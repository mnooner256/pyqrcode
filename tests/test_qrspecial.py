# -*- coding: utf-8 -*-
"""\
Tests against qrspecial.
"""
from __future__ import absolute_import, unicode_literals
from pyqrcode import qrspecial as qrs
try:
    str = unicode
except NameError:
    pass


def test_sms():
    q = qrs.QrShortMessage('+39070653263', 'I like your code!')
    assert 'smsto:+39070653263:I like your code!' == str(q)
    assert q == qrs.QrShortMessage.from_str(str(q))


def test_geo():
    q = qrs.QrGeolocation(42.989, -71.465, 'www.python.org')
    assert 'geo:42.989,-71.465?q=www.python.org' == str(q)
    assert q == qrs.QrGeolocation.from_str(str(q))


def test_mecard():
    q =  qrs.QrContact('Py Thon', email=('py@py.org', 'thon@py.org'))
    assert 'MECARD:N:Py Thon;EMAIL:py@py.org;EMAIL:thon@py.org;;' == str(q)
    assert q == qrs.QrContact.from_str(str(q))


def test_wifi():
    q = qrs.QrWifi('Python', 'WEP', 'Monty', True)
    assert 'WIFI:S:Python;T:WEP;P:Monty;H:true;;' == str(q)
    assert q == qrs.QrWifi.from_str(str(q))


def test_wifi2():
    q = qrs.QrWifi('Python', 'WEP', 'Monty')
    assert 'WIFI:S:Python;T:WEP;P:Monty;;' == str(q)
    assert q == qrs.QrWifi.from_str(str(q))


if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
