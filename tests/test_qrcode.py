# -*- coding: utf-8 -*-
"""\
Different tests against the PyQRCode package.
"""
from __future__ import unicode_literals
import io
from nose.tools import eq_, raises
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
    ('点', 'kanji'),
    ('茗', 'kanji'),
    ('漢字', 'kanji'),
    ('外来語', 'kanji'),
)


def test_valid_mode_autodetection():
    def check(data, expected_mode):
        qr = pyqrcode.create(data)
        eq_(expected_mode, qr.mode)
    for data, mode in _DATA_AUTODETECT:
        yield check, data, mode


def test_valid_mode_provided():
    def check(data, mode):
        qr = pyqrcode.create(data, mode=mode)
        eq_(mode, qr.mode)
    for data, mode in _DATA_AUTODETECT:
        yield check, data, mode


_DATA_INVALID_MODE = (
    # Input, invalid mode
    ('a', 'alphanumeric'),
    ('b', 'numeric'),
    ('C', 'numeric'),
    ('HELLO\nWORLD', 'alphanumeric'),
    ('MÄRCHENBUCH', 'alphanumeric'),
    ('http://www.example.org/', 'alphanumeric'),
    ('http://www.example.org/', 'unknown'),
)


def test_invalid_mode_provided():
    @raises(ValueError)
    def check(data, mode):
        pyqrcode.create(data, mode=mode)
    for data, mode in _DATA_INVALID_MODE:
        yield check, data, mode


def test_binary_data():
    qr = pyqrcode.create('Märchenbuch'.encode('utf-8'))
    eq_('Märchenbuch', qr.data)
    eq_('binary', qr.mode)


def test_unicode_utf8():
    s = '\u263A'  # ☺ (WHITE SMILING FACE)
    try:
        pyqrcode.create(s, encoding='latin1')
        raise Exception('Expected an error for \u263A and ISO-8859-1')
    except ValueError:
        pass
    qr = pyqrcode.create(s, encoding='utf-8')
    eq_('binary', qr.mode)


def test_utf8_detection():
    s = '㋡' #White Smiley face
    qr = pyqrcode.create(s)
    eq_('binary', qr.mode)
    eq_(s.encode('utf-8'), qr.builder.data)


def test_kanji_detection():
    s = '点茗' #Characters directly from the standard
    qr = pyqrcode.create(s)
    qr.png(io.BytesIO(), scale=4)
    eq_('kanji', qr.mode)
    eq_(s.encode('shiftjis'), qr.builder.data)


def test_kanji_enforce_binary():
    data = '点'
    # 1. Try usual mode --> kanji
    qr = pyqrcode.create(data)
    eq_('kanji', qr.mode)
    # 2. Try another encoding --> binary
    qr = pyqrcode.create(data, encoding='utf-8')
    eq_('binary', qr.mode)


def test_kanji_enforce_binary2():
    data = '点'
    qr = pyqrcode.create(data.encode('utf-8'))
    eq_('binary', qr.mode)


def test_to_str():
    py2 = False
    try:
        unicode
        py2 = True
    except NameError:
        pass
    s = 'Märchen'
    qr = pyqrcode.create(s)
    if not py2:
        str(qr)
    else:
        try:
            str(qr)
            raise Exception('No Unicode error?')
        except UnicodeError:
            pass
        unicode(qr)


@raises(ValueError)
def test_invalid_version():
    pyqrcode.create('test', version=41)


@raises(ValueError)
def test_invalid_version2():
    pyqrcode.create('test', version=0)


@raises(ValueError)
def test_invalid_mode():
    pyqrcode.create('test', mode='alpha')


@raises(ValueError)
def test_invalid_mode2():
    pyqrcode.create('test', mode='')


@raises(ValueError)
def test_kanji_not_supported():
    pyqrcode.create('test', mode='kanji')


@raises(ValueError)
def test_invalid_ecc():
    pyqrcode.create('test', error='R')


if __name__ == '__main__':
    import nose
    nose.core.runmodule()
