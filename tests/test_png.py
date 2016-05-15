# -*- coding: utf-8 -*-
"""\
PNG related tests.
"""
from __future__ import unicode_literals, absolute_import
import io
import os
from nose.tools import eq_, raises
import pyqrcode
import png


def test_get_png_size():
    code = pyqrcode.create('Hello world')
    qr_size = 25
    quiet_zone = 0
    eq_(qr_size, code.get_png_size(1, quiet_zone=quiet_zone))
    quiet_zone = 1
    eq_((qr_size + 2 * quiet_zone) * quiet_zone, code.get_png_size(1, quiet_zone=quiet_zone))
    quiet_zone = 4  # (default quiet_zone)
    eq_((qr_size + 2 * quiet_zone) * 1, code.get_png_size())
    eq_((qr_size + 2 * quiet_zone) * 1, code.get_png_size(1))
    eq_((qr_size + 2 * quiet_zone) * 4, code.get_png_size(4))
    quiet_zone = 0
    eq_((qr_size + 2 * quiet_zone) * 4, code.get_png_size(4, quiet_zone=quiet_zone))


def test_get_png_size_scale_int():
    qr = pyqrcode.create('test')
    eq_(21, qr.get_png_size(scale=1, quiet_zone=0))


def test_get_png_size_scale_int2():
    qr = pyqrcode.create('test')
    quiet_zone = 2
    eq_(21 + 2 * quiet_zone, qr.get_png_size(scale=1, quiet_zone=quiet_zone))


def test_get_png_size_scale_float():
    qr = pyqrcode.create('test')
    eq_(21, qr.get_png_size(scale=1.5, quiet_zone=0))


def test_get_png_size_scale_float2():
    qr = pyqrcode.create('test')
    quiet_zone = 2
    eq_(21 + 2 * quiet_zone, qr.get_png_size(scale=1.5, quiet_zone=quiet_zone))
    
def test_png_as_base64_str():
    """\
    Test PNG to Base64 converions using a known Base64 string.
    """
    expected_str = "iVBORw0KGgoAAAANSUhEUgAAAOEAAADhAQAAAAAWyO/XAAACIklEQVR4n"\
                   "O2YMXKrQBBER6WAkCPsTaSLUbVU6WLmJhyBkIDSuLtXxtgu/8DBbwUiQMB"\
                   "TMMzsdM8S+Y9jjBd90b/SJSJOS831upyzu/e3zDc86sy0Zk7LUPKtHyMu/"\
                   "RbdhIDddMAtws17REH0Q8FtlGeguZX10ufcMYn5PDSQSSRR9X0Gqvqec2U"\
                   "S1xOe/ay+gaoXVNWP049O+f9UB9KJ0znjmre5+64qDsqWREERZzCTG35Za"\
                   "TNlkE3IkkJWZ572mE2U637iWuMDLL06U0bmzkwRZFJj78gf6ptzC9xLkUk"\
                   "2J8uLSCG0sbLSnZmOAYOsLYkSD5jSba++jZZ81PeW6wVJXIMeYKZb7AoyB"\
                   "00JHpB7fU2Ui58tidOAnDKxgavOS9mXV7mQTAnplIKYKTQCLSkrOiOTqu/"\
                   "hjVwULXnpR81csTa/zKN3eyi88bRoHAzOOePjyk4RMyRN4oHmpIHv/eGi1"\
                   "A32AiQjPlrj4N0mSpdsVsQ5DMMEZotPNXPRFnM0jaWaJSW3mCmnB6w1Chk"\
                   "kg9NhnKQmXspZXt7N/E34C3Zodc+zi3LBAdAg24ZDs0WaKfSU9dXmJx+T9"\
                   "BBmqkPPtIdVc3Kj7aXal2lnzcD1gWRavu7aHLS2lsR0gw5tBrkcV52H6tu"\
                   "IbrfHK8Rhh2ulQxtXIR7JwOunbngpp5vCj0mRx+nLRVVfDcz6YqNeqHaqX"\
                   "hBN+tFYvs2EFvr78aIv+kf6Dm6Pdk09JdaJAAAAAElFTkSuQmCC"
                   
    qr = pyqrcode.create('Are you suggesting coconuts migrate?')
    generated_str = qr.png_as_base64_str(scale=5)
    eq_(generated_str, expected_str)


_REF_DATA = (
    # Input string, error level, encoding, mode, reference file
    ('Märchenbuch', 'M', 'iso-8859-1', 'binary', 'mb_latin1_m.png'),
    ('Märchenbuch', 'M', 'utf-8',      'binary', 'mb_utf8_m.png'),
    ('Märchenbuch', 'L', 'utf-8',      'binary', 'mb_utf8_l.png'),
    ('Märchenbuch', 'H', 'utf-8',      'binary', 'mb_utf8_h.png'),
    ('Märchenbuch', 'Q', 'utf-8',      'binary', 'mb_utf8_q.png'),
    ('Märchen',     'Q', 'utf-8',      'binary', 'm_utf8_q.png'),
    ('点',           'M', 'shift_jis', 'kanji',  'kanji1_m.png'),
    ('茗',           'M', 'shift_jis', 'kanji',  'kanji2_m.png'),
    ('漢字',         'M', 'shift_jis', 'kanji',  'kanji3_m.png'),
    ('外来語',       'L', 'shift_jis', 'kanji',  'kanji4_l.png'),
)


def test_write_png():
    #
    # How does it work?
    #
    # 1. Generate a PNG with another QR Code generator
    # 2. Safe the PNG into the test/ref directory
    # 3. Add the input string, the error level, the encoding, mode, and
    #    filename to the _REF_DATA dict
    #    The input string, error and encoding is used to create the QR Code.
    #    The mode IS NOT handled over to the QR Code factory function "create"
    #
    # Caution: The "reference file" must have the same dimensions as the
    #          generated image (config: scale = 6, quiet_zone = 4) and must be
    #          black/white.
    #
    # If a generated image isn't equal to the reference file, the error message
    # isn't very helpful, though.
    #
    def check(s, error_level, encoding, expected_mode, reference):
        qr = pyqrcode.create(s, error=err, encoding=encoding)
        eq_(error_level, qr.error)
        eq_(expected_mode, qr.mode)
        scale, quiet_zone = 6, 4
        # Read reference image
        ref_width, ref_height, ref_pixels = _get_png_info(filename=_get_reference_filename(reference))
        # Create our image
        out = io.BytesIO()
        qr.png(out, scale=scale, quiet_zone=quiet_zone)
        out.seek(0)
        # Excpected width/height
        expected_width = qr.get_png_size(scale, quiet_zone)
        # Read created image
        width, height, pixels = _get_png_info(file=out)
        eq_(expected_width, ref_width)
        eq_(expected_width, ref_height)
        eq_(ref_width, width)
        eq_(ref_height, height)
        eq_(len(ref_pixels), len(pixels))
        eq_(ref_pixels, pixels)

    for s, err, encoding, mode, ref in _REF_DATA:
        yield check, s, err, encoding, mode, ref


@raises(ValueError)
def test_hexcolor_too_short():
    qr = pyqrcode.create('test')
    qr.png(io.BytesIO(), module_color='#FFFFF')


@raises(ValueError)
def test_hexcolor_too_short_background():
    qr = pyqrcode.create('test')
    qr.png(io.BytesIO(), background='#FFFFF')


@raises(ValueError)
def test_hexcolor_too_long():
    qr = pyqrcode.create('test')
    qr.png(io.BytesIO(), module_color='#0000000')


@raises(ValueError)
def test_hexcolor_too_long_background():
    qr = pyqrcode.create('test')
    qr.png(io.BytesIO(), background='#0000000')


def png_as_matrix(buff, quiet_zone):
    """\
    Reads the PNG from the provided buffer and returns the code matrix (list
    of lists containing 0 .. 1 values).
    """
    buff.seek(0)
    w, h, pixels = _get_png_info(file=buff)
    # PNG: white = 1, black = 0. QR code: white = 0, black = 1
    fromidx, toidx = quiet_zone, -quiet_zone
    if quiet_zone == 0:
        fromidx = 0
        toidx = len(pixels)
    res = []
    for row in pixels[fromidx:toidx]:
        res.append([(bit - 1) * -1 for bit in row[fromidx:toidx]])
    return res


def _make_pixel_array(pixels, is_greyscale):
    """\
    Returns a list of lists. Each list contains 0 and/or 1.
    0 == black, 1 == white.

    `is_greyscale`
        Indiciates if this function must convert RGB colors into black/white
        (supported values: (0, 0, 0) = black and (255, 255, 255) = white)
    """
    def bw_color(r, g, b):
        rgb = r, g, b
        if rgb == (0, 0, 0):
            return 0
        elif rgb == (255, 255, 255):
            return 1
        else:
            raise ValueError('Unexpected RGB tuple: {0})'.format(rgb))
    res = []
    if is_greyscale:
        for row in pixels:
            res.append(list(row[:]))
    else:
        for row in pixels:
            it = [iter(row)] * 3
            res.append([bw_color(r, g, b) for r, g, b in zip(*it)])
    return res


def _get_reference_filename(filename):
    """\
    Returns an absolute path to the "reference" filename.
    """
    return os.path.join(os.path.dirname(__file__), 'ref/{0}'.format(filename))


def _get_png_info(**kw):
    """\
    Returns the width, height and the pixels of the provided PNG file.
    """
    reader = png.Reader(**kw)
    w, h, pixels, meta = reader.asDirect()
    return w, h, _make_pixel_array(pixels, meta['greyscale'])


if __name__ == '__main__':
    import nose
    nose.core.runmodule()
