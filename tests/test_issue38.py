# -*- coding: utf-8 -*-
"""\
Tests against <https://github.com/mnooner256/pyqrcode/issues/13>
"""
from __future__ import unicode_literals
from nose.tools import eq_
import pyqrcode

def test_long_number_gives_version2():
    code = pyqrcode.create("6010102401", error="H")
    
    eq_(code.version, 1)
    
def test_version_1_max_numeric():
    code = pyqrcode.create("11111111111111111", error="H")
    code.png('test.png', scale=13, quiet_zone=4)
    eq_(code.version, 1)
    
def test_version_1_max_alphanumeric():
    code = pyqrcode.create('ABCDEFGJKL', error="H")
    
    eq_(code.version, 1)
    
def test_version_1_max_kanji():
    code = pyqrcode.create('点点点点', error="H", mode='kanji')
    
    eq_(code.mode, 'kanji')
    eq_(code.version, 1)
    
def test_version_1_max_binary():
    code = pyqrcode.create('ABCDEFG', error="H", mode='binary')
    eq_(code.version, 1)

