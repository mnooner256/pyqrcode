# -*- coding: utf-8 -*-
"""\
Different tests against the PyQRCode package.
"""
from __future__ import unicode_literals
from nose.tools import eq_
import pyqrcode


_DATA_AUTODETECT = (
    # Input, expected version, expected mode
    ('123456', 'numeric'),
    (123456, 'numeric'),
    ('123A', 'alphanumeric'),
    ('123a', 'binary'),
    ('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:', 'alphanumeric'),
    ('HELLO WORLD', 'alphanumeric'),
    ('HELLO\nWORLD', 'binary'),
    ('MÄRCHENBUCH', 'binary'),
    ('®', 'binary'),
    ('http://www.example.org/', 'binary'),
    ('http://www.example.org/path/index.html', 'binary'),
)


def test_valid_mode_autodetection():
    def check(data, expected_mode):
        qr = pyqrcode.create(data)
        eq_(expected_mode, qr.mode)
    for data, mode in _DATA_AUTODETECT:
        yield check, data, mode



_DATA_INVALID_MODE = (
    # Input, invalid mode
    ('a', 'alphanumeric'),
    ('a', 'numeric'),
    ('HELLO\nWORLD', 'alphanumeric'),
    ('MÄRCHENBUCH', 'alphanumeric'),
    ('http://www.example.org/', 'alphanumeric'),
)


def test_invalid_mode_provided():
    def check(data, mode):
        try:
            pyqrcode.create(data, mode=mode)
            raise Exception('Expected an error for create({0}, mode={1})'
                            .format(data, mode))
        except ValueError:
            pass
    for data, mode in _DATA_INVALID_MODE:
        yield check, data, mode


def test_unicode_utf8():
    s = '\u263A'  # ☺ (WHITE SMILING FACE)
    try:
        pyqrcode.create(s, encoding='latin1')
        raise Exception('Expected an error for \u263A and ISO-8859-1')
    except ValueError:
        pass
    qr = pyqrcode.create(s, encoding='utf-8')
    eq_('binary', qr.mode)


if __name__ == '__main__':
    import nose
    nose.core.runmodule()
