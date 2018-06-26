# -*- coding: utf-8 -*-
"""\
Tests against EPS generation.
"""
from __future__ import absolute_import, unicode_literals
import re
import io
import pytest
import pyqrcode


def test_illegal_color_float():
    color = (.1, 1.1, .1)
    qr = pyqrcode.create('test')
    out = io.StringIO()
    with pytest.raises(ValueError):
        qr.eps(out, module_color=color)


def test_illegal_color_float2():
    color = (-.1, 1.0, .1)
    qr = pyqrcode.create('test')
    out = io.StringIO()
    with pytest.raises(ValueError):
        qr.eps(out, module_color=color)


def test_illegal_color_int():
    color = (255, 255, 256)
    qr = pyqrcode.create('test')
    out = io.StringIO()
    with pytest.raises(ValueError):
        qr.eps(out, module_color=color)


def test_illegal_color_int2():
    color = (-1, 1, 1)
    qr = pyqrcode.create('test')
    out = io.StringIO()
    with pytest.raises(ValueError):
        qr.eps(out, module_color=color)


def test_default_color():
    qr = pyqrcode.create('test')
    out = io.StringIO()
    qr.eps(out)
    assert 'setrgbcolor' not in out.getvalue()


def test_module_color():
    qr = pyqrcode.create('test')
    out = io.StringIO()
    qr.eps(out, module_color='#195805')
    assert 'setrgbcolor' in out.getvalue()


def test_module_color_omit_black():
    qr = pyqrcode.create('test')
    out = io.StringIO()
    # Black does not need setrgbcolor since it is the default stroke color
    qr.eps(out, module_color='#000')
    assert 'setrgbcolor' not in out.getvalue()


def test_background():
    qr = pyqrcode.create('test')
    out = io.StringIO()
    qr.eps(out, background='#EEE')
    assert 'setrgbcolor' in out.getvalue()
    assert 'clippath' in out.getvalue()


def test_default_scale():
    qr = pyqrcode.create('test')
    out = io.StringIO()
    qr.eps(out)
    assert 'scale' not in out.getvalue()


def test_scale():
    qr = pyqrcode.create('test')
    out = io.StringIO()
    qr.eps(out, scale=2)
    assert '2 2 scale' in out.getvalue()


def test_scale_float():
    qr = pyqrcode.create('test')
    out = io.StringIO()
    scale = 1.34
    qr.eps(out, scale=scale)
    assert '{0} {0} scale'.format(scale) in out.getvalue()


def eps_as_matrix(buff, quiet_zone):
    """\
    Reads the path in the EPS and returns it as list of 0, 1 lists.
    """
    eps = buff.getvalue()
    h, w = re.search(r'^%%BoundingBox: 0 0 ([0-9]+) ([0-9]+)', eps,
                   flags=re.MULTILINE).groups()
    if h != w:
        raise ValueError('Expected equal height/width, got height="{}" width="{}"'.format(h, w))
    size = int(w) - 2 * quiet_zone
    rows = re.search(r'^newpath[\s+](.+?)(^stroke)', eps,
                  flags=re.DOTALL|re.MULTILINE).group(1).strip().split('\n')
    res = []
    for i, row in enumerate(rows):
        res_row = []
        for x, y, op in re.findall(r'([0-9]+(?:\.[0-9]+)?) ([0-9]+(?:\.[0-9]+)?) ([A-Za-z])', row):
            if op == 'M':
                if int(x) != quiet_zone:
                    raise ValueError('Unexpected quiet_zone width in row "{}". Expected "{}", got "{}"'.format(i, quiet_zone, x))
                continue
            bit = None
            if op == 'l':
                bit = 1
            elif op == 'm':
                bit = 0
            res_row.extend([bit] * int(x))
        # Fill row with zeros if necessary
        res_row.extend([0] * (size - len(res_row)))
        res.append(res_row)
    return res


if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
