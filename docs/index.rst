Welcome to PyQRCode's documentation!
************************************

The pyqrcode module is a QR code generator that is simple to use and written
in pure python 3. The module can automate most of the building process for you.
Unlike other generators, all of these helpers can be controlled manually.
QR codes can be saved as SVG, PNG (by using the
`pypng <https://pypi.python.org/pypi/pypng/>`_ module), and plain text. 

The pyqrcode module attempts to follow the QR code standard as closely as
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
   
   PyPI Readme <README>
   
   glossary
   
Requirements
============

The pyqrcode module only requires Python 3. You may want to install
`pypng <https://pypi.python.org/pypi/pypng/>`_ in order to render PNG files,
but it is optional. Note, pypng is a pure python PNG writer which does not
require any other libraries.


Installation
============

Installation is simple. PyQRCode can be installed from pip using the
following command::

    $ pip install pyqrcode

or from the command line using::

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

The pyqrcode module, while easy to use, is powerful. You can set all of the
properties of the QR code. If you install the optional pypng library, you can
render the code as a PNG image. Below is a more complex example::

    >>> big_code = pyqrcode.create('0987654321', error='L', version=27, mode='binary')
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

