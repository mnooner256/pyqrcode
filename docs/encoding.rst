Encoding Data
*************

The standard calls the data's encoding its :term:`mode`. The QR code standard
defines how to encode any given piece of data. There are 
four possible modes. This module supports three modes:
numeric, alphanumeric, and binary.

.. note::
   The QRCode object can automatically choose the best mode based on the data
   to be encoded. In general, it is best to just let the object figure it out
   for you.

Numeric Encoding
================

The numeric type is the most efficient way to encode digits. Internally, an
integer is converted into a string of digits. You can also specify a string of
digits as the data-type. This encoding is the optimal way to encode digits.

.. code-block:: python

  >>> number = pyqrcode.create(123456789012345)
  >>> number2 = pyqrcode.create('0987654321')

Notice, though that you cannot encode negative or fractional numbers with this
encoding. Instead you would use the Alphanumeric mode.

Alphanumeric
============

The alphanumeric type is very limited in that it can only encode some ASCII
characters. It encodes:

  * Uppercase letters
  * Digits
  * The horizontal space
  * Eight punctuation characters: $, %, \*, +, -, ., /, and :
  
A complete list of the possible characters can be found in the
:py:data:`pyqrcode.tables.ascii_codes` dictionary. While limited, this encoding
is much more efficient for many cases than using the binary encoding. 

.. note::
   The QRCode object will try to use this encoding by using the
   string.upper() method. In other words, it will change the case of input
   if this encoding is selected.

The available characters will let you encode a URL
(the string is uppercased automatically).

.. code-block:: python

  >>> url = pyqrcode.create('http://uca.edu')


Binary
======

When all else fails the data can be encoded in pure binary. This encoding does
not change the data in any way. Instead its pure bytes are represented
directly in the QR code. This is the least efficient way to store data in a 
QR code. You should only use this as a last resort.

The quotation below must be encoded in binary because of the apostrophe and the
new line character.

.. code-block:: python

  >>> life = pyqrcode.create('''MR. CREOSOTE: Better get a bucket. I'm going to throw up.
      MAITRE D: Uh, Gaston! A bucket for monsieur. There you are, monsieur.''')

Kanji
=====

There is one other encoding that is used for Kanji characters. This encoding
is unimplemented at this time because I don't speak Japanese. If anyone wants
to help me write an encoder for Kanji, shoot me an email.

