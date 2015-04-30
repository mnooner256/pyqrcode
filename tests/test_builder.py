# -*- coding: utf-8 -*-
"""\
Test against the buidler module.
"""
from __future__ import unicode_literals
from nose.tools import ok_, eq_, raises
from pyqrcode import builder


def test_illegal_mode():
    try:
        builder.QRCodeBuilder('test', 1, mode='murks', error='M')
        raise Exception('Expected an error for illegal mode')
    except ValueError as ex:
        ok_('murks' in str(ex))


def test_illegal_error():
    try:
        builder.QRCodeBuilder('123', version=40, mode='numeric', error='R')
        raise Exception('Expected an error for illegal mode')
    except ValueError as ex:
        ok_('R' in str(ex))


def test_illegal_version():
    try:
        builder.QRCodeBuilder('123', version=41, mode='numeric', error='M')
        raise Exception('Expected an error for illegal mode')
    except ValueError as ex:
        ok_('41' in str(ex))



if __name__ == '__main__':
    import nose
    nose.core.runmodule()
