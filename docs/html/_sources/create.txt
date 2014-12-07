Creating QR Codes
*****************************************

The QRCode object is designed to be smart about how it constructs QR codes.
It can automatically figure out what mode and version to use to construct a
QR code, based on the data and the amount error correction. The error correction
level defaults to the highest possible level of error correction.

Below are some examples of creating QR Codes using the automatated system.

.. code-block:: python

  >>> url = pyqrcode.create('http://uca.edu')
  >>> url = pyqrcode.create('http://uca.edu', error='L')

There are many situations where you might wish to have more
fine grained control over how the QR Code is generated. You can specify all the
properties of your QR code through the optional parameters of the
:func:`pyqrcode.create` function. There are three main properties to a QR code.

The :term:`error` parameter sets the error correction level of the code. Each
level has an associated name given by a letter: L, M, Q, or H; each level can
correct up to 7, 15, 25, or 30 percent of the data respectively. There are
several ways to specify the level, see :py:data:`pyqrcode.tables.error_level`
for all the possible values. By default this parameter is set to 'H' which is
the highest possible error correction, but it has the smallest available data
capacity for a given version.

The :term:`version` parameter specifies the size and data capacity of the
code. Versions are any integer between 1 and 40. Where version 1 is
the smallest QR code, and version 40 is the largest. By default, the object
uses the data's encoding and error correction level to calculate the smallest
possible version. You may want to specify this parameter for consistency when
generating several QR codes with varying amounts of data. That way all of the
generated codes would have the same size.

Finally, the :term:`mode` parameter sets how the contents will be encoded.
Three of the four possible encodings are available. By default, the object uses
the most efficient encoding for the contents. You can override this behavior
by setting this parameter. See :py:data:`pyqrcode.tables.modes` for a list of
possible values for this parameter. A much longer discussion on modes can be
found in the next section :doc:`encoding`.

The code below constructs a QR code with 25% error correction, size 27, and
forces the encoding to be binary (rather than numeric).

.. code-block:: python

  >>> big_code = pyqrcode.create('0987654321', error='L', version=27, mode='binary')
