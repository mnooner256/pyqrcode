Encoding Data
*************

The standard calls the data's encoding its :term:`mode`. The QR code standard
defines how to encode any given piece of data. There are
four possible modes. This module supports three of them:
numeric, alphanumeric, and binary.

Each mode is worse at encoding the QR code's
contents. In other words, each mode will require more room in the QR code to
store the data. How much data a code version can hold is dependent on what
mode is used and the error correction level. For example, the binary encoding
always requires more code words than the numeric encoding.

Because of this, it is *generally* better to allow the QRCode object to
auto-select the most efficient mode for the code's contents.

.. note::
   The QRCode object can automatically choose the best mode based on the data
   to be encoded. In general, it is best to just let the object figure it out
   for you.

Numeric Encoding
================

The numeric type is the most efficient way to encode digits. Problematically,
the standard make no provisions for encoding negative or fractional numbers.
This encoding is better than Alphanumeric, when you only have a list of
digits.

To use this encoding, simply specify a string of digits as the data.
You can also use a positive integer as the code's contents.

.. code-block:: python

  >>> number = pyqrcode.create(123456789012345)
  >>> number2 = pyqrcode.create('0987654321')

Alphanumeric
============

The alphanumeric type is very limited in that it can only encode some ASCII
characters. It encodes:

* Uppercase letters
* Digits 0-9
* The horizontal space
* Eight punctuation characters: $, %, \*, +, -, ., /, and :

A complete list of the possible characters can be found in the
:py:data:`pyqrcode.tables.ascii_codes` dictionary. While limited, this encoding
is much more efficient than using the binary encoding, in many cases.

.. note::
   The QRCode object will try to use this encoding by using the
   string.upper() method. In other words, it will change the case of input
   if this encoding is selected. If the content's case matters then be sure
   to explicitly set the mode to binary.

Luckily, the available characters will let you encode a URL
(the string is uppercased automatically).

.. code-block:: python

  >>> url = pyqrcode.create('http://uca.edu')


Binary
======

When all else fails the data can be encoded in pure binary. This encoding does
not change the data in any way. Instead its pure bytes are represented
directly in the QR code. This is the least efficient way to store data in a
QR code. You should only use this as a last resort.

The quotation below must be encoded in binary because of the apostrophe,
exclamation point, and the new line character. Notice, that the string's
characters will not have their case changed.

.. code-block:: python

  >>> life = pyqrcode.create('''MR. CREOSOTE: Better get a bucket. I'm going to throw up.
      MAITRE D: Uh, Gaston! A bucket for monsieur. There you are, monsieur.''')

Kanji
=====

There is one other encoding. This mode is used for Kanji characters. This
mode is unimplemented at this time because I don't speak Japanese. If anyone
wants to help me write an encoder for Kanji, shoot me an email.
