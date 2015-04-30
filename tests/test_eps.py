# -*- coding: utf-8 -*-
"""\
Tests against EPS generation.
"""
from __future__ import absolute_import, unicode_literals
import re
import io
from nose.tools import ok_, raises
import pyqrcode


@raises(ValueError)
def test_illegal_color_float():
    color = (.1, 1.1, .1)
    qr = pyqrcode.create('test')
    out = io.StringIO()
    qr.eps(out, module_color=color)


@raises(ValueError)
def test_illegal_color_float2():
    color = (-.1, 1.0, .1)
    qr = pyqrcode.create('test')
    out = io.StringIO()
    qr.eps(out, module_color=color)


@raises(ValueError)
def test_illegal_color_int():
    color = (255, 255, 256)
    qr = pyqrcode.create('test')
    out = io.StringIO()
    qr.eps(out, module_color=color)


@raises(ValueError)
def test_illegal_color_int2():
    color = (-1, 1, 1)
    qr = pyqrcode.create('test')
    out = io.StringIO()
    qr.eps(out, module_color=color)


def test_default_color():
    qr = pyqrcode.create('test')
    out = io.StringIO()
    qr.eps(out)
    ok_('setrgbcolor' not in out.getvalue())


def test_module_color():
    qr = pyqrcode.create('test')
    out = io.StringIO()
    qr.eps(out, module_color='#195805')
    ok_('setrgbcolor' in out.getvalue())


def test_module_color_omit_black():
    qr = pyqrcode.create('test')
    out = io.StringIO()
    # Black does not need setrgbcolor since it is the default stroke color
    qr.eps(out, module_color='#000')
    ok_('setrgbcolor' not in out.getvalue())


def test_background():
    qr = pyqrcode.create('test')
    out = io.StringIO()
    qr.eps(out, background='#EEE')
    ok_('setrgbcolor' in out.getvalue())
    ok_('clippath' in out.getvalue())


def test_default_scale():
    qr = pyqrcode.create('test')
    out = io.StringIO()
    qr.eps(out)
    ok_('scale' not in out.getvalue())


def test_scale():
    qr = pyqrcode.create('test')
    out = io.StringIO()
    qr.eps(out, scale=2)
    ok_('2 2 scale' in out.getvalue())


def test_scale_float():
    qr = pyqrcode.create('test')
    out = io.StringIO()
    scale = 1.34
    qr.eps(out, scale=scale)
    ok_('{0} {0} scale'.format(scale) in out.getvalue())


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
    import nose
    nose.core.runmodule()
