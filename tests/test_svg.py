# -*- coding: utf-8 -*-
"""\
Tests against SVG generation.
"""
from __future__ import absolute_import, unicode_literals
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


if __name__ == '__main__':
    import nose
    nose.core.runmodule()
