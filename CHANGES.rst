Changes
=======

1.3.2 - 2019-06-29
------------------
* Initial release of PyQRCode NG (PyQRCode Next Generation)


1.3.0 - 2018-06-26
------------------
* Added support for meCards etc. contributed by Riccardo Metere
  Fixed <https://github.com/mnooner256/pyqrcode/pull/45>
* Skip detecting content type if constructor mode is given to constructor.
  Contributed by Martijn van Rheenen.
  Fixed <https://github.com/mnooner256/pyqrcode/issues/50>
* Moved tests from nose to pytest since nose is deprecated,
  see <https://github.com/heuer/pyqrcode/issues/2>
* Updated test environment: Added PyPy, PyPy3 and Python 3.6
* QRCode.get_png_size() is deprecated, use QRCode.symbol_size(). The latter
  returns a (width, height) tuple, not an integer.
* Deprecated QRCode.png_as_base64_str(), use QRCode.png_data_uri() which returns
  a valid URI instead of a Base64 encoded string
* Faster PNG generation, fixed <https://github.com/mnooner256/pyqrcode/pull/47>
* Added CLI
  Fixed #4 and <https://github.com/mnooner256/pyqrcode/pull/53>
* Added term() method to QRCode which prints the QR Code to the terminal.
  This works with Windows and Unix.
* Deprecated QRCode.terminal() in favor of QRCode.term()
* Added "scale" parameter to QRCode.text


1.2.1 - 2016-06-20
------------------
* Fixed issue #43. A debug print statement got left in by mistake. I altered
  The distribution script to check and make sure it does not happen again.


1.2 - 2016-05-20
----------------
* Added Kanji support.
* Added ability to output PNG QR codes as a base64 string. Allows coded to be
  created for web services without the need to create intermediary files.
  Thanks to [Fábio C. Barrionuevo da Luz (luzfcb)](https://github.com/luzfcb)
* Added renderer for XBM. Displaying QR codes in Tkinter is now extremely
  simple. Thanks to [Seth VanHeulen (svanheulen)](https://github.com/svanheulen)


1.1.1 - 2016-02-27
------------------
* Fix for issue #38, where numeric encodings got broken by added unicode support.


1.1 - 2016-04-15
----------------
* Added support for Python 2.6
* All renderers now have a **quiet zone of four**. This value is settable via a
  parameter.
* Fixed issue where file streams were not being closed correctly
* **Special thanks goes to [Lars (heuer)](https://github.com/heuer) who 
  contributed a massive amount of improvements in this version.**

  * Enormously improved SVG implementation. Now uses paths instead of lines.
    Also allows for SVG fragments instead of entire documents.
  * We now have unit tests!! He wrote over 100 unit tests for
    all of the various parts of the library.
  * A new EPS renderer.
  * A mechanism for showing QR codes directly from within your code.


1.0 - 2014-12-04
----------------
* Fixed issue where terminal bits were being added in the wrong location.
* Added ability to output QR code to a Linux terminal.
* Added support for Python 2.7
