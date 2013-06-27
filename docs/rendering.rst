Rendering QR Codes
******************

There are three possible formats for rendering the QR Code. The first is
to render it as a string of 1's and 0's. This is method is available so
a user can create their own renderer. There are also two image based
renderers. Both allow you to set the colors used. They also take a scaling
factor, that way each module is not rendered as 1 pixel.

Text Rendering
==============

The module includes a text renderer. This will return a string containing the
QR code as a string of 1's and 0's, with each row of the code on a new line.
The purpose of this renderer is to allow users to create their own renderer if
neither the svg or png renderers are satisfactory.

.. code-block:: python

  >>> number = pyqrcode.create(123)
  >>> print(number.text())
  00000000000000000000000
  01111111001101011111110
  01000001000111010000010
  01011101001011010111010
  01011101000110010111010
  01011101010100010111010
  01000001001111010000010
  01111111010101011111110
  00000000010110000000000
  00011001111000110100000
  01100100110001110001110
  01001111001110110010100
  00111010111010001111110
  00000001111010101001000
  00000000010010100010010
  01111111010110001000110
  01000001000100011101100
  01011101001110111110010
  01011101010100001111100
  01011101011110011000000
  01000001000110101001000
  01111111000001010100100
  00000000000000000000000

Image Rendering
===============

There are two ways to get an image of the generated QR code. Both renderers 
have a few things in common.

Both renderers take a file path or writable file stream and draw the QR
code there. The methods should auto-detect what to do.

Both renderers take a scale parameter. This parameter sets how many pixels a
single data module will take. Usually setting this parameter to one, will result
in QR codes that are too small to scan. What scale to use depends on how you
plan to use the QR code.

Both renderers, also, allow you to set the module and background colors.
Although, how the colors are represented differ.

Scalable Vector Graphic
-----------------------

The SVG renderer outputs the QR Code as a scalable vector graphic. *This
renderer does not require any external modules.*

The method draws the QR code using a set of horizontal lines. By default, no
background is drawn, i.e. the resulting code has a transparent background. The
default foreground color is black.

.. code-block:: python

  >>> url = pyqrcode.create('http://uca.edu')
  >>> url.svg(sys.stdout, scale=1)
  >>> url.svg('uca.svg', scale=4)
  
You can change the colors of the data-modules using the *module* parameter.
Likewise, you can specify a background using the *background* parameter. Each
of these parameters take a HTML style color.

.. code-block:: python

  >>> url.svg('uca.svg', scale=4, background="white", module_color="#7D007D")

Portable Network Graphic
------------------------

The png() method takes a file path or writable stream and outputs the QR code
as a PNG.

.. note::

  This method requires the `pypng <https://pypi.python.org/pypi/pypng/>`_ module.

Colors should be a list or tuple containing number between zero an 255. The
lists should be of length three (for RGB) or four (for RGBA). The color (0,0,0)
represents black. A value of zero for the fourth element, represents full
transparency. Likewise, a value of 255 for the fourth element represents full
opacity.

By default, the png() method creates a QR code with the data modules colored
black, and the background modules colored white.

.. code-block:: python

  >>> url.png('uca.png')
  >>> colors.png('uca.png', scale=6, module_color=[0, 0, 0, 128], background=[0xff, 0xff, 0xcc])

