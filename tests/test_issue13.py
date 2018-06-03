# -*- coding: utf-8 -*-
"""\
Tests against <https://github.com/mnooner256/pyqrcode/issues/13>
"""
from __future__ import unicode_literals
import pyqrcode


def test_binary_detection():
    code = pyqrcode.create('Hello world')
    assert 'binary' == code.mode


def test_alphanumeric_detection():
    code = pyqrcode.create('HELLO WORLD')
    assert 'alphanumeric' == code.mode


if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
