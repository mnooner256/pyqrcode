# -*- coding: utf-8 -*-
"""\
Differnt output tests.
"""
from __future__ import unicode_literals, absolute_import
import io
from nose.tools import eq_
import pyqrcode
try:
    from .test_eps import eps_as_matrix
    from .test_png import png_as_matrix
    from .test_svg import svg_as_matrix
except ValueError:  # Attempted relative import in non-package
    from test_eps import eps_as_matrix
    from test_png import png_as_matrix
    from test_svg import svg_as_matrix


_DATA = (
    # Input string, error level, quiet_zone
    ('Märchenbuch', 'M', 4),
    (123, 'H', 0),
    ('http:/www.example.org/', 'L', 3),
    ('Hello\nWorld', 'Q', 2),
    ('HELLO WORLD', 'H', 2),
)

def test_data():
    # Creates a QR code, serializes it and checks if the serialization
    # corresponds to the initial QR code matrix.
    def check(serializer_name, buffer_factory, to_matrix_func, data, error, quiet_zone):
        """\
        `serializer_name`
            Method name to serialize the QR code
        `buffer_factory`
            Callable to construct the buffer.
        `to_matrix_func`
            Function to convert the buffer back to a matrix.
        `data`
            The input to construct the QR code.
        `error`
            ECC level
        `quiet_zone`
            quiet_zone size.
        """
        qr = pyqrcode.create(data, error=error)
        out = buffer_factory()
        meth = getattr(qr, serializer_name)
        meth(out, quiet_zone=quiet_zone)
        matrix = to_matrix_func(out, quiet_zone)
        eq_(qr.code, matrix)
    for meth_name, buffer_factory, to_matrix_func in (('eps', io.StringIO, eps_as_matrix),
                                                      ('png', io.BytesIO, png_as_matrix),
                                                      ('svg', io.BytesIO, svg_as_matrix)):
        for data, error, quiet_zone in _DATA:
            yield check, meth_name, buffer_factory, to_matrix_func, data, error, quiet_zone


if __name__ == '__main__':
    import nose
    nose.core.runmodule()
