# -*- coding: utf-8 -*-
"""\
Tests against <https://github.com/mnooner256/pyqrcode/issues/15>
"""
from __future__ import unicode_literals
import pyqrcodeng as pyqrcode


def test_create_numeric():
    code = pyqrcode.create(666)
    assert 'numeric' == code.mode


def test_create_numeric_from_string():
    code = pyqrcode.create('666')
    assert 'numeric' == code.mode


if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
