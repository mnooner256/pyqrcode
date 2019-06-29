Welcome to PyQRCodeNG's documentation!
*********************```**************

The PyQRCodeNG module is a QR code generator that is simple to use and written
in pure python. The module is compatible with Python 2.6, 2.7, and 3.x. The
module automates most of the building process for you. Generally, QR codes can
be created using only two lines of code!

Unlike many other generators, all of the automation can be controlled manually.
You are free to set any or all of the properties of your QR code.

QR codes can be saved as SVG, EPS, PNG (by using the
`pypng <https://pypi.org/project/pypng/>`_ module), and plain text. PIL is
not used to render the image files. You can also display a QR code directly in
a compatible terminal.

The PyQRCodeNG module attempts to follow the QR code standard as closely as
possible. The terminology and the encodings used in pyqrcode come directly
from the standard. This module also follows the algorithm laid out in the
standard.

Contents:

.. toctree::
   :maxdepth: 1

   create
   encoding
   rendering
   moddoc
   glossary

Requirements
============

The PyQRCodeNG module only requires Python 2.6, 2.7, 3.x. You may want to
install `pypng <https://pypi.org/project/pypng/>`_ in order to render PNG
files, but it is optional. Note, pypng is a pure python PNG writer which does
not require any other libraries.


Installation
============

Installation is simple. PyQRCodeNG can be installed from pip using the
following command::

    $ pip install -U pyqrcodeng


Usage
=====

The PyQRCodeNG module aims to be as simple to use as possible. Below is a simple
example of creating a QR code for a URL. The code is rendered out as a black
and white scalable vector graphics file.
::

    >>> import pyqrcodeng
    >>> url = pyqrcodeng.create('http://uca.edu')
    >>> url.svg('uca-url.svg', scale=8)
    >>> print(url.terminal(quiet_zone=1))

The PyQRCodeNG module, while easy to use, is powerful. You can set all of the
properties of the QR code. If you install the optional pypng library, you can
also render the code as a PNG image. Below is a more complex example::

    >>> big_code = pyqrcodeng.create('0987654321', error='L', version=27, mode='binary')
    >>> big_code.png('code.png', scale=6, module_color=[0, 0, 0, 128], background=[0xff, 0xff, 0xcc])


Developer Documentation
=======================

.. toctree::
   :maxdepth: 1

   moddoc
   tables
   builder


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
