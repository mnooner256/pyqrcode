Rendering QR Codes
******************

There are three possible formats for rendering the QR Code. The first is
to render it as a string of 1's and 0's. There are also two image based
renderers. Both allow you to set the colors used. They also take a scaling
factor, that way each module is not rendered as 1 pixel.

Text Rendering
==============

The pyqrcode module includes a text renderer. This will return a string
containing the QR code as a string of 1's and 0's, with each row of the code on
a new line. A :term:`data module` in the QR Code is represented by a 1.
Likewise, 0 is used to represent the background of the code.

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

Terminal Rendering
==================

QR codes can be directly rendered to a compatible terminal in a
manner readable by QR code scanners. Most Linux terminals are supported. This
is done using ASCII escape codes. The QR code's colors can even be set.

.. code-block:: python

  >>> text = pyqrcode.create('Example')
  >>> print(text.terminal())
  >>> print(text.terminal(module_color='red', background='yellow'))
  >>> print(text.terminal(module_color=5, background=123))

Rendering colors in a terminal is a tricky business. Beyond the eight named
colors, compatability becomes problematic. With this in mind it is best to
stick to the eight well known colors: black, red, green, yellow, blue, magenta,
and cyan. Although, these colors are also supported on almost every color 
terminal: light gray, dark gray, light red, light green, light blue, light
yellow, light magenta, light cyan, and white. There are two additional named
colors.

The first is "default" it corresponds to the default background color
of the terminal. The other is "reverse", this inverts the current background
color. These are the default colors used by the terminal method.

The terminal method also support the 256 color scheme. This is the least
transportable of the color schemes. To use this color scheme simply supply a
number between 0 and 256. This number will act as an index to the terminal's
color pallete. What color that index actually corresponds to is system
dependent. In other words, while most terminal emulators support 256 colors,
the there is no way to tell what color will be actually displayed.


Image Rendering
===============

There are two ways to get an image of the generated QR code. Both renderers 
have a few things in common.

Both renderers take a file path or writable file stream and draw the QR
code there. The methods should auto-detect which is which.

Each renderer takes a scale parameter. This parameter sets the size of a single
:term:`data module` in pixels. Setting this parameter to one, will
result in each :term:`data module` taking up 1 pixel. In other words, the QR
code would be too small to scan. What scale to use depends on how you plan to
use the QR code. Generally, three, four, or five will result in small but
scanable QR codes.

Both renderers, also, allow you to set the :term:`module` and background colors.
Although, how the colors are represented are renderer specific.

Scalable Vector Graphic
-----------------------

The SVG renderer outputs the QR code as a scalable vector graphic using
the :py:meth:`pyqrcode.QRCode.svg` method. *This
renderer does not require any external modules.*

The method draws the QR code using a set of horizontal lines. By default, no
background is drawn, i.e. the resulting code has a transparent background. The
default foreground color is black.

.. code-block:: python

  >>> url = pyqrcode.create('http://uca.edu')
  >>> url.svg(sys.stdout, scale=1)
  >>> url.svg('uca.svg', scale=4)
  
You can change the colors of the data-modules using the *module_color*
parameter. Likewise, you can specify a background using the *background*
parameter. Each of these parameters take a HTML style color.

.. code-block:: python

  >>> url.svg('uca.svg', scale=4, background="white", module_color="#7D007D")

Portable Network Graphic
------------------------

The PNG renderer ouputs the QR code as a portable network graphic file using
the :py:meth:`pyqrcode.QRCode.png` method.

.. note::

  This renderer requires the `pypng <https://pypi.python.org/pypi/pypng/>`_
  module.

.. code-block:: python

  >>> url = pyqrcode.create('http://uca.edu')
  >>> with open('code.png', 'w') as fstream:
  ...     url.png(fstream, scale=5)


Colors should be a list or tuple containing numbers between zero an 255. The
lists should be of length three (for RGB) or four (for RGBA). The color (0,0,0)
represents black and the color (255,255,255) represents white. A value of zero
for the fourth element, represents full transparency. Likewise, a value of 255
for the fourth element represents full opacity.

By default, the renderer creates a QR code with the data modules colored
black, and the background modules colored white.

.. code-block:: python

  >>> url.png('uca-colors.png', scale=6, module_color=[0, 0, 0, 128], background=[0xff, 0xff, 0xcc])

