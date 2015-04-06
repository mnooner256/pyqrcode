# -*- coding: utf-8 -*-
"""\
PNG related tests.
"""
from __future__ import unicode_literals
import os
import io
from nose.tools import eq_
import pyqrcode
try:
    import png
except ImportError:
    from pyqrcode import png


def test_size():
    code = pyqrcode.create('Hello world')
    qr_size = 25
    border = 0
    eq_(qr_size, code.get_png_size(1, border=border))
    border = 1
    eq_((qr_size + 2 * border) * border, code.get_png_size(1, border=border))
    border = 4  # (default border)
    eq_((qr_size + 2 * border) * 1, code.get_png_size())
    eq_((qr_size + 2 * border) * 1, code.get_png_size(1))
    eq_((qr_size + 2 * border) * 4, code.get_png_size(4))
    border = 0
    eq_((qr_size + 2 * border) * 4, code.get_png_size(4, border=border))


_REF_DATA = (
    # Input string, error level, encoding, reference file
    ('Märchenbuch', 'M', 'iso-8859-1', 'mb_latin1_m.png'),
    ('Märchenbuch', 'M', 'utf-8', 'mb_utf8_m.png'),
    ('Märchenbuch', 'L', 'utf-8', 'mb_utf8_l.png'),
    ('Märchenbuch', 'H', 'utf-8', 'mb_utf8_h.png'),
    ('Märchenbuch', 'Q', 'utf-8', 'mb_utf8_q.png'),
)


def _make_pixel_array(pixels, greyscale):
    """\
    Returns a list of lists. Each list contains 0 and/or 1.
    0 == black, 1 == white.

    `greyscale`
        Indiciates if this function must convert RGB colors into black/white.
    """
    def bw_color(r, g, b):
        rgb = r, g, b
        if rgb == (0, 0, 0):
            return 0
        elif rgb == (255, 255, 255):
            return 1
        else:
            raise ValueError('Unexpected RGB tuple %r' % rgb)
    res = []
    if greyscale:
        for row in pixels:
            res.append(list(row[:]))
    else:
        for row in pixels:
            it = [iter(row)] * 3
            res.append([bw_color(r, g, b) for r, g, b in zip(*it)])
    return res


def test_write_png():
    def check(qr, reference):
        scale, border = 6, 4
        reader = png.Reader(filename=os.path.join(os.path.dirname(__file__), 'ref/{}'.format(reference)))
        # Read reference image
        ref_width, ref_height, ref_pixels, meta = reader.asDirect()
        ref_pixels = _make_pixel_array(ref_pixels, meta['greyscale'])
        # Create our image
        out = io.BytesIO()
        qr.png(out, scale=scale, border=border)
        # Excpected width/height
        expected_width = qr.get_png_size(scale, border)
        out.seek(0)
        # Read created image
        reader = png.Reader(file=out)
        width, height, pixels, meta = reader.asDirect()
        pixels = _make_pixel_array(pixels, meta['greyscale'])
        eq_(expected_width, ref_width)
        eq_(expected_width, ref_height)
        eq_(ref_width, width)
        eq_(ref_height, width)
        eq_(len(ref_pixels), len(pixels))
        eq_(ref_pixels, pixels)

    for s, err, encoding, ref in _REF_DATA:
        qr = pyqrcode.create(s, error=err, encoding=encoding)
        yield check, qr, ref


if __name__ == '__main__':
    import nose
    nose.core.runmodule()
