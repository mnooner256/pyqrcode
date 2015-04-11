# -*- coding: utf-8 -*-
"""\
Tests against EPS generation.
"""
from __future__ import absolute_import, unicode_literals
import re
import io
from nose.tools import eq_, raises
import pyqrcode


_DATA = (
    # Input string, error level, border
    ('Märchenbuch', 'M', 4),
    (123, 'H', 0),
    ('http:/www.example.org/', 'L', 3),
    ('Hello\nWorld', 'Q', 2),
)

def test_data():
    def check(data, error, border):
        qr = pyqrcode.create(data, error=error)
        out = io.StringIO()
        qr.eps(out, border=border)
        eps_matrix = _eps_as_matrix(out.getvalue(), border)
        eq_(qr.code, eps_matrix)
    for data, error, border in _DATA:
        yield check, data, error, border


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


def _eps_as_matrix(eps, border):
    """\
    Reads the path in the EPS string and returns it as list of 0, 1 lists.
    """
    h, w = re.search(r'^%%BoundingBox: 0 0 ([0-9]+) ([0-9]+)', eps,
                   flags=re.MULTILINE).groups()
    if h != w:
        raise ValueError('Expected equal height/width, got height="{}" width="{}"'.format(h, w))
    size = int(w) - 2 * border
    rows = re.search(r'^newpath[\s+](.+?)(^stroke)', eps,
                  flags=re.DOTALL|re.MULTILINE).group(1).strip().split('\n')
    res = []
    for i, row in enumerate(rows):
        res_row = []
        for x, y, op in re.findall(r'([0-9]+(?:.[0-9]+)?) ([0-9]+(?:.[0-9]+)?) ([A-Za-z])', row):
            if op == 'M':
                if int(x) != border:
                    raise ValueError('Unexpected border width in row "{}". Expected "{}", got "{}"'.format(i, border, x))
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
