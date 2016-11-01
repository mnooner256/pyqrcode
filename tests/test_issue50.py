# -*- coding: utf-8 -*-
"""\
Tests against <https://github.com/mnooner256/pyqrcode/issues/50>
"""
from __future__ import unicode_literals
from nose.tools import eq_
import pyqrcode


class FakeString:
    '''
    Create a mock class that *acts* like a string as far as needed for the QRCode constructor,
    but raises an exception in case shiftjis encoding is used on its value.

    This mimics the behaviour of Python on an environment where this codec is not installed.
    '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    def __len__(self):
        return len(self.value)

    def encode(self, encoding):
        if encoding == 'shiftjis':
            raise LookupError("unknown encoding: shiftjis")
        return self.value.encode(encoding)


def test_constructing_without_shiftjis_encoding_available():
    content = FakeString("t123456789")
    code = pyqrcode.create(content, error="Q")
    eq_(code.mode, 'binary')
