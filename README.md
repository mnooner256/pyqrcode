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
------------

Installation is simple. It can be installed from pip using the following command:

```bash
$ pip install pyqrcode
```

or from the code

```bash
$ python setup.py install
```

Usage
-----

This is the only import you need. The QRCode class will build the code and
render the QR code.

```python
>>> from pyqrcode import QRCode
```

### Encoding Data ###

This module supports three encodings for data: numeric, alphanumeric, and
binary. The numeric type is the most efficient way to encode digits. You can
use a string containing only digits instead of an actual number.

```python
>>> number = QRCode(123456789012345)
````

The alphanumeric type is very limited in that it can only encode some ASCII
characters. It encodes: uppercase letters, 0-9, the horizontal space, and eight
punctuation characters. To see a complete list of the possible characters that
can be encoded see the pyqrcode.tables.ascii_codes dictionary. The available
characters will let you encode a URL (the string is uppercased automatically).

```python
>>> url = QRCode('http://uca.edu')
```

When all else fails the data can be encoded in pure binary. The quotation below
must be encoded in binary because of the apostrophe and the new line character.

```python
>>> life = QRCode('''MR. CREOSOTE: Better get a bucket. I'm going to throw up.
    MAITRE D: Uh, Gaston! A bucket for monsieur. There you are, monsieur.''')
```
There is one other encoding for Kanji characters, this is unimplemented at this
time because I don't speak Japanese. If anyone wants to help me write an
encoder for Kanji, shoot me an email.

### Manually Setting The QR Code's Properties ###

There are many situation where you might wish to have more fine grained control
over how the QR Code is generated. You can specify all the properties of your
QR code through the QRCode constructor. There are three main properties to a
QR code.

The _error_ parameter sets the error correction level of the code. Each level
has an associated name given by a letter: L, M, Q, H; each level can correct up
to 7, 15, 25, or 30 percoent of the data respectively. There are several ways
to specify the level, see pyqrcode.tables.modes for all the possible
values. By default this parameter is set to 'H' which is the highest
possible error correction, but it has the smallest available data
capacity.

The _version_ parameter specifies the size and data capacity of the
code. Versions are any integer between 1 and 40. Where version 1 is
the smallest QR code, and version 40 is the largest. By default, the object
uses the data's encoding and error correction level to calculate the smallest
possible version. You may want to specify this parameter for consistency when
generating several QR codes with varying amounts of data. That way all of the
generated codes would have the same size.

Finally, the _mode_ parameter sets how the contents will be encoded. As
mentioned above three of the four possible encodings have been written. By
default the object uses the most efficient encoding for the contents. You can
change this though. See qrcode.tables.modes for a list of possible values
for this parameter.
        
The code below constructs a QR code with 30% error correction, size 27, and
forces the encoding to be binary (rather than numeric).

```python
>>> big_code = QRCode(123456789, error='L', version=27, mode='binary')
```

### Rendering ###

There are three possible formats for rendering the QR Code. The first is
to render it as a string of 1's and 0's. This is method is available so
a user can create their own renderer. There are also two image based
renderers. Both allow you to set the colors used. They also take a scaling
factor, that way each module is not rendered as 1 pixel.

The SVG renderer outputs the QR Code as a scalable vector graphic. This
renderer does not require any external modules. Instead it hand draws the
QR code as a set of lines.

```python    
>>> url.svg(sys.stdout, scale=1)
>>> url.svg('uca.svg', scale=4, module_color="#7D007D")
```

Alternatively, if you install the pypng module, you can render the QR Code
to a PNG file. Colors should be specified as RGB or RGBA if you want to
take advantage of transparency.

```python
>>> number.png('big-number.png')
>>> life.png('sketch.png', scale=6, module_color=[0, 0, 0, 128], background=[0xff, 0xff, 0xcc])
```    
Finally, there is a text based renderer. This will output the QR code as a
string of 1's and 0's, with each row of the code on a new line.

```python
>>> print(number.text())
```
