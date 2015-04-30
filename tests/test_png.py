# -*- coding: utf-8 -*-
"""\
PNG related tests.
"""
from __future__ import unicode_literals, absolute_import
import io
from nose.tools import eq_
import pyqrcode
try:
    from . import utils
except (ValueError, SystemError):
    import utils


def test_size():
    code = pyqrcode.create('Hello world')
    qr_size = 25
    border = 0
    eq_(qr_size, code.get_png_size(1, quiet_zone=border))
    border = 1
    eq_((qr_size + 2 * border) * border, code.get_png_size(1, quiet_zone=border))
    border = 4  # (default border)
    eq_((qr_size + 2 * border) * 1, code.get_png_size())
    eq_((qr_size + 2 * border) * 1, code.get_png_size(1))
    eq_((qr_size + 2 * border) * 4, code.get_png_size(4))
    border = 0
    eq_((qr_size + 2 * border) * 4, code.get_png_size(4, quiet_zone=border))


_REF_DATA = (
    # Input string, error level, encoding, reference file
    ('Märchenbuch', 'M', 'iso-8859-1', 'mb_latin1_m.png'),
    ('Märchenbuch', 'M', 'utf-8', 'mb_utf8_m.png'),
    ('Märchenbuch', 'L', 'utf-8', 'mb_utf8_l.png'),
    ('Märchenbuch', 'H', 'utf-8', 'mb_utf8_h.png'),
    ('Märchenbuch', 'Q', 'utf-8', 'mb_utf8_q.png'),
    ('Märchen',     'Q', 'utf-8', 'm_utf8_q.png'),
)


def test_write_png():
    def check(s, error_level, encoding, reference):
        qr = pyqrcode.create(s, error=err, encoding=encoding)
        eq_(error_level, qr.error)
        scale, border = 6, 4
        # Read reference image
        ref_width, ref_height, ref_pixels = utils.get_png_info(filename=utils.get_reference_filename(reference))
        # Create our image
        out = io.BytesIO()
        qr.png(out, scale=scale, quiet_zone=border)
        out.seek(0)
        # Excpected width/height
        expected_width = qr.get_png_size(scale, border)
        # Read created image
        width, height, pixels = utils.get_png_info(file=out)
        eq_(expected_width, ref_width)
        eq_(expected_width, ref_height)
        eq_(ref_width, width)
        eq_(ref_height, height)
        eq_(len(ref_pixels), len(pixels))
        eq_(ref_pixels, pixels)

    for s, err, encoding, ref in _REF_DATA:
        yield check, s, err, encoding, ref


if __name__ == '__main__':
    import nose
    nose.core.runmodule()
