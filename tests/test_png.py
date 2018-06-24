# -*- coding: utf-8 -*-
"""\
PNG related tests.
"""
from __future__ import unicode_literals, absolute_import
import io
import os
import pytest
import pyqrcode
import png


def test_get_png_size():
    code = pyqrcode.create('Hello world')
    qr_size = 25
    quiet_zone = 0
    assert qr_size == code.get_png_size(1, quiet_zone=quiet_zone)
    quiet_zone = 1
    assert (qr_size + 2 * quiet_zone) * quiet_zone == code.get_png_size(1, quiet_zone=quiet_zone)
    quiet_zone = 4  # (default quiet_zone)
    assert (qr_size + 2 * quiet_zone) * 1 == code.get_png_size()
    assert (qr_size + 2 * quiet_zone) * 1 ==  code.get_png_size(1)
    assert (qr_size + 2 * quiet_zone) * 4 == code.get_png_size(4)
    quiet_zone = 0
    assert (qr_size + 2 * quiet_zone) * 4 == code.get_png_size(4, quiet_zone=quiet_zone)


def test_symbol_size():
    code = pyqrcode.create('Hello world')
    dim = 25
    quiet_zone = 0
    assert (dim, dim) == code.symbol_size(1, quiet_zone=quiet_zone)
    quiet_zone = 1
    d = (dim + 2 * quiet_zone) * quiet_zone
    assert (d, d) == code.symbol_size(1, quiet_zone=quiet_zone)
    quiet_zone = 4  # (default quiet_zone)
    d = (dim + 2 * quiet_zone) * 1
    assert (d, d) == code.symbol_size()
    assert (d, d) ==  code.symbol_size(1)
    d = (dim + 2 * quiet_zone) * 4
    assert d, d == code.symbol_size(4)
    quiet_zone = 0
    d = (dim + 2 * quiet_zone) * 4
    assert (d, d) == code.symbol_size(4, quiet_zone=quiet_zone)


def test_symbol_size_scale_int():
    qr = pyqrcode.create('test')
    dim = 21
    assert (dim, dim) == qr.symbol_size(scale=1, quiet_zone=0)


def test_symbol_size_scale_int2():
    qr = pyqrcode.create('test')
    quiet_zone = 2
    dim = 21 + 2 * quiet_zone
    assert (dim, dim) == qr.symbol_size(scale=1, quiet_zone=quiet_zone)


def test_symbol_size_scale_float():
    qr = pyqrcode.create('test')
    dim = 21 * 1.5
    assert (dim, dim) == qr.symbol_size(scale=1.5, quiet_zone=0)


def test_symbol_size_scale_float2():
    qr = pyqrcode.create('test')
    quiet_zone = 2
    dim = (21 + 2 * quiet_zone) * 1.5
    assert (dim, dim) == qr.symbol_size(scale=1.5, quiet_zone=quiet_zone)


def test_png_as_base64_str():
    """\
    Test PNG to Base64 converions using a known Base64 string.
    """
    expected_str = 'iVBORw0KGgoAAAANSUhEUgAAALkAA' \
                   'AC5AQAAAABc1qPxAAABZUlEQVR42u1XMW7DMBCj60GjnqCf2B8z' \
                   'YAP+mP0TP8GjBsNXUk07tVvBAG00CEluoO6Ox2MQ358Fr8AfDpw' \
                   'AunMqGPKCtPFbYuANP5xfDAh8jtgFPvKKnU9ygk9Iu2pw54vgJ4' \
                   'ob/JwPXn08BTzWI7Ychx1cPY8LdWTtk7vnD7Ynsc7N9nbO/ki6v' \
                   'mbQ1/MKtruObHeo+9aylzpgKrUj5fnL7ASPNUizq4hwvKQ0RvAF' \
                   'dciN43yBGmAm3JYvyXrfuObMnHPOnUJl1ZTVzjvnLDY6Nh4jlYY' \
                   'v8BJuAQZWPG0f6fdW8EvFXkqjPJ8xO0Um4mDFQ4uFbGf3YSXcwc' \
                   'yZNDLTvwHrnF+EJC5HfMGn5zISrs25KC95nYp9q8lCaKU+Vpt3n' \
                   '88hGyUvBS/hmnvl5ybwNHJ2D0fcO1Pm1PNwu1dC3tSXtlKfYJ2l' \
                   '7aWlb3evEVrlLHte/WxX2TXsgxf89d/5nwXeAQ4lThIyLqhcAAA' \
                   'ANHRFWHRTb2Z0d2FyZQBTZWdubyA8aHR0cHM6Ly9weXBpLnB5dG' \
                   'hvbi5vcmcvcHlwaS9zZWduby8+6uNDygAAAABJRU5ErkJggg=='
                   
    qr = pyqrcode.create('Are you suggesting coconuts migrate?', error='m')
    generated_str = qr.png_as_base64_str(scale=5)
    assert expected_str == generated_str


def test_png_uri():
    """\
    Test PNG to Base64 converions using a known Base64 string.
    """
    expected_str = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAALkAA' \
                   'AC5AQAAAABc1qPxAAABZUlEQVR42u1XMW7DMBCj60GjnqCf2B8z' \
                   'YAP+mP0TP8GjBsNXUk07tVvBAG00CEluoO6Ox2MQ358Fr8AfDpw' \
                   'AunMqGPKCtPFbYuANP5xfDAh8jtgFPvKKnU9ygk9Iu2pw54vgJ4' \
                   'ob/JwPXn08BTzWI7Ychx1cPY8LdWTtk7vnD7Ynsc7N9nbO/ki6v' \
                   'mbQ1/MKtruObHeo+9aylzpgKrUj5fnL7ASPNUizq4hwvKQ0RvAF' \
                   'dciN43yBGmAm3JYvyXrfuObMnHPOnUJl1ZTVzjvnLDY6Nh4jlYY' \
                   'v8BJuAQZWPG0f6fdW8EvFXkqjPJ8xO0Um4mDFQ4uFbGf3YSXcwc' \
                   'yZNDLTvwHrnF+EJC5HfMGn5zISrs25KC95nYp9q8lCaKU+Vpt3n' \
                   '88hGyUvBS/hmnvl5ybwNHJ2D0fcO1Pm1PNwu1dC3tSXtlKfYJ2l' \
                   '7aWlb3evEVrlLHte/WxX2TXsgxf89d/5nwXeAQ4lThIyLqhcAAA' \
                   'ANHRFWHRTb2Z0d2FyZQBTZWdubyA8aHR0cHM6Ly9weXBpLnB5dG' \
                   'hvbi5vcmcvcHlwaS9zZWduby8+6uNDygAAAABJRU5ErkJggg=='

    qr = pyqrcode.create('Are you suggesting coconuts migrate?', error='m')
    generated_str = qr.png_data_uri(scale=5)
    assert expected_str == generated_str


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


@pytest.mark.parametrize('s, error_level, encoding, expected_mode, reference', _REF_DATA)
def test_write_png(s, error_level, encoding, expected_mode, reference):
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
    qr = pyqrcode.create(s, error=error_level, encoding=encoding)
    assert error_level == qr.error
    assert expected_mode == qr.mode
    scale, quiet_zone = 6, 4
    # Read reference image
    ref_width, ref_height, ref_pixels = _get_png_info(filename=_get_reference_filename(reference))
    # Create our image
    out = io.BytesIO()
    qr.png(out, scale=scale, quiet_zone=quiet_zone)
    out.seek(0)
    # Excpected width/height
    expected_width, expected_height = qr.symbol_size(scale, quiet_zone)
    # Read created image
    width, height, pixels = _get_png_info(file=out)
    assert expected_width == ref_width
    assert expected_height == ref_height
    assert ref_width == width
    assert ref_height == height
    assert len(ref_pixels) == len(pixels)
    assert ref_pixels == pixels


def test_hexcolor_too_short():
    qr = pyqrcode.create('test')
    with pytest.raises(ValueError):
        qr.png(io.BytesIO(), module_color='#FFFFF')


def test_hexcolor_too_short_background():
    qr = pyqrcode.create('test')
    with pytest.raises(ValueError):
        qr.png(io.BytesIO(), background='#FFFFF')


def test_hexcolor_too_long():
    qr = pyqrcode.create('test')
    with pytest.raises(ValueError):
        qr.png(io.BytesIO(), module_color='#0000000')


def test_hexcolor_too_long_background():
    qr = pyqrcode.create('test')
    with pytest.raises(ValueError):
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
    pytest.main([__file__])
