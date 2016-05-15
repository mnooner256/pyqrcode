========
PyQRCode
========

.. contents::

The pyqrcode module is a QR code generator that is simple to use and written
in pure python. The module can automates most of the building process for
creating QR codes. Most codes can be created using only two lines of code!

Unlike other generators, all of the helpers can be controlled manually. You are
free to set any or all of the properties of your QR code.

QR codes can be saved as SVG, PNG (by using the
`pypng <https://pypi.python.org/pypi/pypng/>`_ module), and plain text. They can
also be displayed directly in most Linux terminal emulators. PIL is
not used to render the image files.

The pyqrcode module attempts to follow the QR code standard as closely as
possible. The terminology and the encodings used in pyqrcode come directly
from the standard. This module also follows the algorithm laid out in the
standard.

**Homepage**: https://github.com/mnooner256/pyqrcode

**Documentation**: http://pythonhosted.org/PyQRCode/

Requirements
============

The pyqrcode module only requires Python 2.6, Python 2.7, or Python 3. You may
want to install `pypng <https://pypi.python.org/pypi/pypng/>`_ in order to
render PNG files, but it is optional. Note, pypng is a pure python PNG writer
which does not require any other libraries.

Installation
============

Installation is simple. It can be installed from pip using the following
command::

    $ pip install pyqrcode

Or from the terminal::

    $ python setup.py install


Usage
=====

The pyqrcode module aims to be as simple to use as possible. Below is a simple
example of creating a QR code for a URL. The code is rendered out as an svg
file.
::

    >>> import pyqrcode
    >>> url = pyqrcode.create('http://uca.edu')
    >>> url.svg('uca-url.svg', scale=8)
    >>> url.eps('uca-url.eps', scale=2)
    >>> print(url.terminal(quiet_zone=1))

The pyqrcode module, while easy to use, is powerful. You can set every
property of the QR code. If you install the optional
`pypng <https://pypi.python.org/pypi/pypng/>`_ module, you can
render the code as a PNG image. Below is a more complex example::

    >>> big_code = pyqrcode.create('0987654321', error='L', version=27, mode='binary')
    >>> big_code.png('code.png', scale=6, module_color=[0, 0, 0, 128], background=[0xff, 0xff, 0xcc])
    >>> big_code.show()
