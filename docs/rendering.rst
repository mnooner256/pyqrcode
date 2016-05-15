Rendering QR Codes
******************

There are five possible formats for rendering the QR Code. The first is
to render it as a string of 1's and 0's. Next, the code can be displayed
directly in compatible terminals. There are also three image based
renderers. All, but the first, allow you to set the colors used. They also
take a scaling factor, that way each module is not rendered as 1 pixel.

Text Based Rendering
====================

The pyqrcode module includes a basic text renderer. This will return a string
containing the QR code as a string of 1's and 0's, with each row of the code on
a new line. A :term:`data module` in the QR Code is represented by a 1.
Likewise, 0 is used to represent the background of the code.

The purpose of this renderer is to allow users to create their own renderer if
none of the built in renderers are satisfactory.

.. code-block:: python

  >>> number = pyqrcode.create(123)
  >>> print(number.text())
  00000000000000000000000000000
  00000000000000000000000000000
  00000000000000000000000000000
  00000000000000000000000000000
  00001111111011110011111110000
  00001000001000101010000010000
  00001011101001010010111010000
  00001011101010011010111010000
  00001011101000100010111010000
  00001000001001001010000010000
  00001111111010101011111110000
  00000000000001011000000000000
  00000010111011010100010010000
  00001011110001111101010010000
  00000111111011100101001000000
  00001001100011010011110010000
  00001111111001101011001110000
  00000000000010000000001100000
  00001111111000111100100100000
  00001000001011010110001100000
  00001011101010110000101010000
  00001011101001111111010100000
  00001011101011101001011010000
  00001000001001011001110000000
  00001111111000011011011010000
  00000000000000000000000000000
  00000000000000000000000000000
  00000000000000000000000000000
  00000000000000000000000000000


Terminal Rendering
==================

QR codes can be directly rendered to a compatible terminal in a
manner readable by QR code scanners.  The rendering is done using ASCII escape
codes. Hence, most Linux terminals are supported. The QR code's colors can even
be set.

.. code-block:: python

  >>> text = pyqrcode.create('Example')
  >>> print(text.terminal())
  >>> print(text.terminal(module_color='red', background='yellow'))
  >>> print(text.terminal(module_color=5, background=123, quiet_zone=1))

Rendering colors in a terminal is a tricky business. Beyond the eight named
colors, compatibility becomes problematic. With this in mind it is best to
stick to the eight well known colors: black, red, green, yellow, blue, magenta,
and cyan. Although, these colors are also supported on almost every color 
terminal: light gray, dark gray, light red, light green, light blue, light
yellow, light magenta, light cyan, and white.

There are two additional named colors. The first is "default" it corresponds to
the default background color of the terminal. The other is "reverse", this
inverts the current background color. These are the default colors used by the
terminal method.

The terminal method also support the 256 color scheme. This is the least
transportable of the color schemes. To use this color scheme simply supply a
number between 0 and 256. This number will act as an index to the terminal's
color palette. What color that index actually corresponds to is system
dependent. In other words, while most terminal emulators support 256 colors,
the there is no way to tell what color will be actually displayed.

Image Rendering
===============

There are three ways to get an image of the generated QR code. All of the
renderers have a few things in common.

Each renderer takes a file path or writable stream and draws the QR
code there. The methods should auto-detect which is which.

Each renderer takes a scale parameter. This parameter sets the size of a single
:term:`data module` in pixels. Setting this parameter to one, will
result in each :term:`data module` taking up 1 pixel. In other words, the QR
code would be too small to scan. What scale to use depends on how you plan to
use the QR code. Generally, three, four, or five will result in small but
scanable QR codes.

QR codes are also supposed to have a :term:`quiet zone` around them. This area
is four modules wide on each side. The purpose of the quiet zone is to make
scanning a printed area more reliable. For electronic usages, this may be
unnecessary depending on how the code is being displayed. Each of the renderers
allows you to set the size of the quiet zone.

Many of the renderers, also, allow you to set the :term:`module` and background
colors. Although, how the colors are represented are renderer specific.

XBM Rendering
-------------

The XBM file format is a simple black and white image format. The image data
takes the form of a valid C header file. XBM rendering is handled via the
:py:meth:`pyqrcode.QRCode.xbm` method.

XMB's are natively supported by Tkinter. This makes displaying QR codes in a
Tkinter application very simple.

.. code-block:: python

    >>> import pyqrcode
    >>> import tkinter
    >>> # Create and render the QR code
    >>> code = pyqrcode.create('Knights who say ni!')
    >>> code_xbm = code.xbm(scale=5)
    >>> # Create a tk window
    >>> top = tkinter.Tk()
    >>> # Make generate the bitmap image from the redered code
    >>> code_bmp = tkinter.BitmapImage(data=code_xbm)
    >>> # Set the code to have a white background,
    >>> # instead of transparent
    >>> code_bmp.config(background="white")
    >>> # Bitmaps are accepted by lots of Widgets
    >>> label = tkinter.Label(image=code_bmp)
    >>> # The QR code is now visible
    >>> label.pack()

Scalable Vector Graphic (SVG)
-----------------------------

The SVG renderer outputs the QR code as a scalable vector graphic using
the :py:meth:`pyqrcode.QRCode.svg` method.

The method draws the QR code using a set of paths. By default, no background is
drawn, i.e. the resulting code has a transparent background. The
default foreground (module) color is black.

.. code-block:: python

  >>> url = pyqrcode.create('http://uca.edu')
  >>> url.svg('uca.svg', scale=4)
  >>> # in-memory stream is also supported
  >>> buffer = io.BytesIO()
  >>> url.svg(buffer)
  >>> # do whatever you want with buffer.getvalue()
  >>> print(list(buffer.getvalue()))
  
You can change the colors of the data-modules using the *module_color*
parameter. Likewise, you can specify a background using the *background*
parameter. Each of these parameters take a HTML style color.

.. code-block:: python

  >>> url.svg('uca.svg', scale=4, background="white", module_color="#7D007D")

You can also suppress certain parts of the SVG document. In other words you
can create a SVG fragment.

Encapsulated PostScript (EPS)
-----------------------------

The EPS renderer outputs the QR code an encapsulated PostScript document using
the :py:meth:`pyqrcode.QRCode.eps` method. *This renderer does not require any
external modules.*

The method draws the EPS document using lines of contiguous modules. By default,
no background is drawn, i.e. the resulting code has a transparent background.
The default module color is black. Note, that a scale of 1 equates to a module
being drawn at 1 point (1/72 of an inch).

.. code-block:: python

  >>> qr = pyqrcode.create('Hello world')
  >>> qr.eps('hello-world.eps', scale=2.5, module_color='#36C')
  >>> qr.eps('hello-world2.eps', background='#eee')
  >>> out = io.StringIO()
  >>> qr.eps(out, module_color=(.4, .4, .4))

Portable Network Graphic (PNG)
------------------------------

The PNG renderer outputs the QR code as a portable network graphic file using
the :py:meth:`pyqrcode.QRCode.png` method.

.. note::

  This renderer requires the `pypng <https://pypi.python.org/pypi/pypng/>`_
  module.

.. code-block:: python

  >>> url = pyqrcode.create('http://uca.edu')
  >>> with open('code.png', 'w') as fstream:
  ...     url.png(fstream, scale=5)
  >>> # same as above
  >>> url.png('code.png', scale=5)
  >>> # in-memory stream is also supported
  >>> buffer = io.BytesIO()
  >>> url.png(buffer)
  >>> # do whatever you want with buffer.getvalue()
  >>> print(list(buffer.getvalue()))


Colors should be a list or tuple containing numbers between zero an 255. The
lists should be of length three (for RGB) or four (for RGBA). The color (0,0,0)
represents black and the color (255,255,255) represents white. A value of zero
for the fourth element, represents full transparency. Likewise, a value of 255
for the fourth element represents full opacity.

By default, the renderer creates a QR code with the data modules colored
black, and the background modules colored white.

.. code-block:: python

  >>> url.png('uca-colors.png', scale=6, 
  ...         module_color=[0, 0, 0, 128], 
  ...         background=[0xff, 0xff, 0xcc])

