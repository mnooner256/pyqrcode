# -*- coding: utf-8 -*-
"""\
Tests against <https://github.com/mnooner256/pyqrcode/issues/17> and
<https://github.com/heuer/pyqrcode/issues/10>

Unicode issues.
"""
from __future__ import unicode_literals
import pyqrcodeng as pyqrcode


def test_issue_10_17():
    qr = pyqrcode.create('John’s Pizza')
    assert qr
    assert 'binary' == qr.mode


if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
