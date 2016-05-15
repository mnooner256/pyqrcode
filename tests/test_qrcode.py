# -*- coding: utf-8 -*-
"""\
Different tests against the PyQRCode package.
"""
from __future__ import unicode_literals
from nose.tools import eq_, raises, ok_
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
    qr = pyqrcode.create('Märchenbuch'.encode('utf-8'), encoding='utf-8')
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

def test_kanji_detection():
    s = '点茗' #Characters directly from the standard
    qr = pyqrcode.create(s)
    eq_('kanji', qr.mode)
    eq_(s.encode('shiftjis'), qr.builder.data)

def test_kanji_encoding():
    s = '点茗' #Characters directly from the standard

    #These come from a reference image passed through the debugger
    codewords = [128,38,207,234,168,0,236,17,236,18,75,55,241,75,140,21,
                 117,174,242,221,243,87,199,123,50,169]
    
    qr = pyqrcode.create(s)

    #Get the binary representation of the data for the code
    bin_words = qr.builder.buffer.getvalue()

    #Convert the data into integer bytes
    b = [int(bin_words[i:i+8], base=2) for i in range(0, len(bin_words), 8)]

    #See if the calculated code matches the known code
    eq_(b, codewords)
    
def test_kanji_tranform_encoding():
    """Test the encoding can be set to shiftjis for utf-8 encoding.
    """
    s = 'モンティ'
    s = '点茗' #Characters directly from the standard
    
    #Encode the string as utf-8 *not* shiftjis
    utf8 = s.encode('utf-8')
    
    qr = pyqrcode.create(utf8, encoding='utf-8')
    
    eq_(qr.mode, 'kanji')
    eq_(qr.encoding, 'shiftjis')
    

def test_kanji_enforce_binary():
    data = '点'
    # 1. Try usual mode --> kanji
    qr = pyqrcode.create(data)
    eq_('kanji', qr.mode)
    # 2. Try another encoding --> binary
    qr = pyqrcode.create(data, mode='binary', encoding='utf-8')
    eq_('binary', qr.mode)


def test_kanji_enforce_binary2():
    data = '点'
    qr = pyqrcode.create(data.encode('utf-8'))
    eq_('binary', qr.mode)


def test_kanji_bytes():
    data = '外来語'
    qr = pyqrcode.create(data.encode('shift_jis'))
    eq_('kanji', qr.mode)

def test_to_str():
    s = 'Märchen'
    ok_(str(pyqrcode.create(s)))

    s = '外来語'
    qr = pyqrcode.create(s)
    ok_(str(pyqrcode.create(s)))


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
