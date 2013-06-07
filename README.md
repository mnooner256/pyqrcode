pyqrcode
================================

The pyqrcode module is a QR code generator that is simple to use and written
in pure python. The module has the ability to choose the best encoding for your
data automatically. You can also specify the error correction level. The module
can also choose the smallest QR code to fit your data automatically. All of
these helpers can be controlled manually.

The pyqrcode module attempts to follow the QR code standard as closely as
possible. The terminology and the encodings used in pyqrcode come directly
from the standard. This module also follows the algorithm laid out in the
standard.

Requirements
-------------------------

The pyqrcode module only requires Python 3. You may want to install pypng in
order to render PNG files, but it is optional.

Installation
-------------------------

Installation is simple. It can be installed from pip using the following command:

```python
$ pip install pyqrcode
```

or from the code

```bash
$ python setup.py install
```

Example Usage
-------------------------

This is the only import you need. The QRCode class will build the code and
render the QR code.

```python
>>> from pyqrcode import QRCode
```

This module supports three encodings for data: numeric, alphanumeric, and
binary. The numeric type is the most efficient way to encode digits.::

```python
>>> number = QRCode(123456789012345)
````

The alphanumeric type is very limited in that it can only encode some ASCII
characters. It encodes: uppercase letters, 0-9, the horizontal space, and eight
punctuation characters. To see a complete list of the possible characters that
can be encoded see the pyqrcode.tables.ascii_codes dictionary. The available
characters will let you encode a URL (the string is uppercased automatically).::

```python
>>> url = QRCode('http://uca.edu')
```

When all else fails the data can be encoded in pure binary. The quotation below
must be encoded in binary because of the apostrophe and the new line character.::

```python
>>> life = QRCode('''MR. CREOSOTE: Better get a bucket. I'm going to throw up.
    MAITRE D: Uh, Gaston! A bucket for monsieur. There you are, monsieur.''')
```
There is one other encoding for Kanji characters, this is unimplemented at this
time because I don't speak Japanese. If anyone wants to help me write an
encoder for Kanji, shoot me an email.

You want to specify all the properties of your QR code through the constructor.
The code below constructs a QR code with 30% error correction, size 27, and
forces the encoding to be binary (rather than numeric).::

```python
>>> big_code = QRCode(123456789, error='L', version=27, mode='binary')
```

There are three possible formats for rendering the QR Code. The first is
to render it as a string of 1's and 0's. This is method is available so
a user can create their own renderer. There are also two image based
renderers. Both allow you to set the colors used. They also take a scaling
factor, that way each module is not rendered as 1 pixel.

The SVG renderer outputs the QR Code as a scalable vector graphic. This
renderer does not require any external modules. Instead it hand draws the
QR code as a set of lines.::

```python    
>>> url.svg(sys.stdout, scale=1)
>>> url.svg('uca.svg', scale=4, module_color="#7D007D")
```

Alternatively, if you install the pypng module, you can render the QR Code
to a PNG file. Colors should be specified as RGB or RGBA if you want to
take advantage of transparency.::

```python
>>> number.png('big-number.png')
>>> life.png('sketch.png', scale=6, module_color=[0, 0, 0, 128], background=[0xff, 0xff, 0xcc])
```    

