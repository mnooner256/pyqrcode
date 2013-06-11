.. contents::

========
PyQRCode
========

The pyqrcode module is a QR code generator that is simple to use and written
in pure python. The module has the ability to choose the best encoding for your
data automatically. You can also specify the error correction level. The module
can also choose the smallest QR code to fit your data automatically. All of
these helpers can be controlled manually.

The pyqrcode module attempts to follow the QR code standard as closely as
possible. The terminology and the encodings used in pyqrcode come directly
from the standard. This module also follows the algorithm laid out in the
standard.

**Homepage**: https://github.com/mnooner256/pyqrcode

**Documentation**: http://pythonhosted.org/PyQRCode/

Requirements
============

The pyqrcode module only requires Python 3. You may want to install pypng in
order to render PNG files, but it is optional.

Installation
============

Installation is simple. It can be installed from pip using the following command::

    $ pip install pyqrcode

or from the code::

    $ python setup.py install


Usage
=====

The pyqrcode module aims to be as simple to use as possible. Below is a simple
example of creating a QR code for a URL. The code is rendered out as an svg
file.
::

    >>> from pyqrcode import QRCode
    >>> url = QRCode('http://uca.edu')
    >>> url.svg('uca-url.svg', scale=8)

The pyqrcode module, while easy to use, is powerful. You can set all of the
properties of your code. If you install the optional pypng library, you can
render the code as a PNG image. Below is a more complex example::

    >>> big_code = QRCode('0987654321', error='L', version=27, mode='binary')
    >>> big_code.png('code.png', scale=6, module_color=[0, 0, 0, 128], background=[0xff, 0xff, 0xcc])

