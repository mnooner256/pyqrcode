# -*- coding: utf-8 -*-
"""\
Tests against SVG generation.
"""
from __future__ import absolute_import, unicode_literals
import re
import io
import xml.etree.ElementTree as etree
from nose.tools import eq_, ok_
import pyqrcode

_SVG_NS = 'http://www.w3.org/2000/svg'


def _get_path(root):
    return root.find('{%s}path' % _SVG_NS)


def _get_title(root):
    return root.find('{%s}title' % _SVG_NS)


def _parse_xml(buff):
    """\
    Parses XML and returns the root element.
    """
    buff.seek(0)
    return etree.parse(buff).getroot()


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
        out = io.BytesIO()
        qr.svg(out, border=border)
        path_matrix = _path_as_matrix(out, border)
        eq_(qr.code, path_matrix)
    for data, error, border in _DATA:
        yield check, data, error, border


def test_write_svg():
    # Test with default options
    qr = pyqrcode.create('test')
    out = io.BytesIO()
    qr.svg(out)
    xml_str = out.getvalue().decode('utf-8')
    ok_(xml_str.startswith('<?xml'))
    root = _parse_xml(out)
    ok_('viewBox' not in root.attrib)
    ok_('height' in root.attrib)
    ok_('width' in root.attrib)
    css_class = root.attrib.get('class')
    ok_(css_class)
    eq_('pyqrcode', css_class)
    path_el = _get_path(root)
    ok_(path_el is not None)
    path_class = path_el.get('class')
    eq_('pyqrline', path_class)
    stroke = path_el.get('stroke')
    eq_('#000', stroke)
    title_el = _get_title(root)
    ok_(title_el is None)


def test_write_no_xmldecl():
    qr = pyqrcode.create('test')
    out = io.BytesIO()
    qr.svg(out, xmldecl=False)
    xml_str = out.getvalue().decode('utf-8')
    ok_(xml_str.startswith('<svg'))


def test_viewbox():
    qr = pyqrcode.create('test')
    out = io.BytesIO()
    qr.svg(out, omithw=True)
    root = _parse_xml(out)
    ok_('viewBox' in root.attrib)
    ok_('height' not in root.attrib)
    ok_('width' not in root.attrib)


def test_no_svg_class():
    qr = pyqrcode.create('test')
    out = io.BytesIO()
    qr.svg(out, svgclass=None)
    root = _parse_xml(out)
    ok_('class' not in root.attrib)


def test_custom_svg_class():
    qr = pyqrcode.create('test')
    out = io.BytesIO()
    qr.svg(out, svgclass='test-class')
    root = _parse_xml(out)
    ok_('class' in root.attrib)
    eq_('test-class', root.attrib.get('class'))


def test_no_line_class():
    qr = pyqrcode.create('test')
    out = io.BytesIO()
    qr.svg(out, lineclass=None)
    root = _parse_xml(out)
    path_el = _get_path(root)
    ok_('class' not in path_el.attrib)


def test_custom_line_class():
    qr = pyqrcode.create('test')
    out = io.BytesIO()
    qr.svg(out, lineclass='test-class')
    root = _parse_xml(out)
    path_el = _get_path(root)
    ok_('class' in path_el.attrib)
    eq_('test-class', path_el.attrib.get('class'))


def test_omit_svgns():
    qr = pyqrcode.create('test')
    out = io.BytesIO()
    qr.svg(out, svgns=False)
    root = _parse_xml(out)
    path_el = _get_path(root)
    ok_(path_el is None)  # (since _get_path uses the SVG namespace)
    path_el = root.find('path')  # Query w/o namespace MUST find the path
    ok_(path_el is not None)


def test_title():
    qr = pyqrcode.create('test')
    out = io.BytesIO()
    qr.svg(out, title='Test')
    root = _parse_xml(out)
    title_el = _get_title(root)
    ok_(title_el is not None)
    eq_('Test', title_el.text)


def test_title2():
    qr = pyqrcode.create('test')
    out = io.BytesIO()
    qr.svg(out, title='Määhhh')
    root = _parse_xml(out)
    title_el = _get_title(root)
    ok_(title_el is not None)
    eq_('Määhhh', title_el.text)


def _path_as_matrix(buff, border):
    """\
    Returns the QR code path as list of [0,1] lists.
    """
    root = _parse_xml(buff)
    path = _get_path(root)
    h = root.attrib['height']
    w = root.attrib['width']
    if h != w:
        raise ValueError('Expected equal height/width, got height="{}" width="{}"'.format(h, w))
    size = int(w) - 2 * border
    d = path.attrib['d']
    res = []
    res_row = None
    absolute_x = -border
    for op, x, y, l in re.findall(r'([Mm])(\-?[0-9]+(?:\.[0-9]+)?) (\-?[0-9]+(?:\.[0-9]+)?)h([0-9]+)', d):
        x = int(x)
        y = float(y)
        l = int(l)
        if y != 0.0:  # New row
            if res_row is not None:
                res_row.extend([0] * (size - len(res_row)))
            res_row = []
            res.append(res_row)
        if op == 'm':
            absolute_x += x
            if x < 0:
                res_row.extend([0] * absolute_x)
            else:
                res_row.extend([0] * x)
            absolute_x += l
        elif op == 'M':
            absolute_x = l
            if x != border:
                raise ValueError('Unexpected border width. Expected "{}", got "{}"'.format(border, x))
        res_row.extend([1] * l)
    res_row.extend([0] * (size - len(res_row)))
    return res


if __name__ == '__main__':
    import nose
    nose.core.runmodule()
