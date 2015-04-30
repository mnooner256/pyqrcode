pyqrcode
================================

The pyqrcode module is a QR code generator that is simple to use and written
in pure python. The module can automates most of the building process for
creating QR codes. Most codes can be created using only two lines of code!

Unlike other generators, all of the helpers can be controlled manually. You are
free to set any or all of the properties of your QR code.

QR codes can be saved as SVG, PNG (by using the
[pypng](https://pypi.python.org/pypi/pypng/) module), or plain text. They can
also be displayed directly in most Linux terminal emulators. PIL is
not used to render the image files.

The pyqrcode module attempts to follow the QR code standard as closely as
possible. The terminology and the encodings used in pyqrcode come directly
from the standard. This module also follows the algorithm laid out in the
standard.

Requirements
-------------------------

The pyqrcode module only requires Python 2.6, Python 2.7 or Python 3. You may
want to install pypng in order to render PNG files, but it is optional.

Installation
------------

Installation is simple. It can be installed from pip using the following
command:

```bash
$ pip install pyqrcode
```

or from the code

```bash
$ python setup.py install
```

Usage
-----

This is the only import you need. The heart of the module is the QRCode class.
You can construct the class normally, or use the *create* wrapper function.

```python
>>> import pyqrcode
```

PyPi
----

* _PyPi page_: https://pypi.python.org/pypi?name=PyQRCode&:action=display

* _Documentation_: http://pythonhosted.org/PyQRCode/

### Encoding Data ###

This module supports three encodings for data: numeric, alphanumeric, and
binary. The numeric type is the most efficient way to encode digits. As the
name implies it is designed to encode integers. Some numbers might be two
large, the object can use a string containing only digits instead of an
actual number.

```python
>>> number = pyqrcode.create(123456789012345)
````

The alphanumeric type is very limited in that it can only encode some ASCII
characters. It encodes: uppercase letters, 0-9, the horizontal space, and eight
punctuation characters. A complete list of the possible characters that
can be encoded can be found in the  pyqrcode.tables.ascii_codes dictionary. The
available characters will let you encode a URL (note that you have to transform
the characters to upper-case otherwise the ``create`` function will use the
``binary`` encoding automatically).


```python
>>> url = pyqrcode.create('http://uca.edu'.upper())
```

When all else fails the data can be encoded in pure binary. The quotation below
must be encoded in binary because of the lower-cased characters, the apostrophe
and the new line character.

```python
>>> life = pyqrcode.create('''MR. CREOSOTE: Better get a bucket. I'm going to throw up.
    MAITRE D: Uh, Gaston! A bucket for monsieur. There you are, monsieur.''')
```
There two other encodings that are unimplemented. The first is used for Kanji
characters. This encoding is unimplemented at this time because I don't speak
Japanese. If anyone wants to help me write an encoder for Kanji, shoot me an
email. The other is ECI mode which allows for multiple encodings in one QR
code (this will be implemented in a future version).

### Manually Setting The QR Code's Properties ###

There are many situation where you might wish to have more fine grained control
over how the QR Code is generated. You can specify all the properties of your
QR code through the *create* function. There are three main properties to a
QR code.

The _error_ parameter sets the error correction level of the code. Each level
has an associated name given by a letter: L, M, Q, or H; each level can
correct up to 7, 15, 25, or 30 percent of the data respectively. There are
several ways to specify the level, see pyqrcode.tables.modes for all the
possible values. By default this parameter is set to 'H' which is the highest
possible error correction, but it has the smallest available data
capacity.

The _version_ parameter specifies the size and data capacity of the
code. Versions are any integer between 1 and 40, where version 1 is
the smallest QR code, and version 40 is the largest. By default, the object
uses the data's encoding and error correction level to calculate the smallest
possible version. You may want to specify this parameter for consistency when
generating several QR codes with varying amounts of data. That way all of the
generated codes would have the same size.

Finally, the _mode_ parameter sets how the contents will be encoded. As
mentioned above, three of the five possible encodings have been written. By
default the object uses the most efficient encoding for the contents. You can
change this though. See qrcode.tables.modes for a list of possible values
for this parameter.

The code below constructs a QR code with 25% error correction, size 27, and
forces the encoding to be binary (rather than numeric).

```python
>>> big_code = pyqrcode.create('0987654321', error='L', version=27, mode='binary')
```

### Rendering ###

There are four possible formats for rendering the QR Code. The first is
to render it as a string of 1's and 0's. This is method is used to help end
users create their own renderer. It is also possible to print the
code such that it is directly displayable in most Linux terminals.
There are also two image based renderers. Both allow you to set the colors
used. They also take a scaling factor, that way each module is not rendered as
1 pixel.

The terminal renderer outputs a string of ASCII escape codes that when
displayed in a compatible terminal, will display a valid QR code. The
background and module colors are settable (although as with any time you display
colors in the terminal, there are several caveats).

```python
>>> print(url.terminal())
>>> print(url.terminal('red', 'white'))
```

The SVG renderer outputs the QR Code as a scalable vector graphic. This
renderer does not require any external modules. Instead it hand draws the
QR code as a set paths.

```python
>>> url.svg(sys.stdout, scale=1)
>>> url.svg('uca.svg', scale=4, module_color="#7D007D")
```

Alternatively, if you install the pypng module, you can render the QR Code
to a PNG file. Colors should be specified as RGB or RGBA if you want to
take advantage of transparency.

```python
>>> number.png('big-number.png')
>>> life.png('sketch.png', scale=6, module_color=(0, 0, 0, 128), background=(0xff, 0xff, 0xcc))
```

Finally, there is a text based renderer. This will output the QR code as a
string of 1's and 0's, with each row of the code on a new line.

```python
>>> print(number.text())
```
