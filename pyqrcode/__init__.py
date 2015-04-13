# -*- coding: utf-8 -*-
"""This module is used to create QR Codes. It is designed to be as simple and
as possible. It does this by using sane defaults and autodetection to make
creating a QR Code very simple.

It is recommended that you use the :func:`pyqrcode.create` function to build the
QRCode object. This results in cleaner looking code.

Examples:
        >>> import pyqrcode
        >>> import sys
        >>> url = pyqrcode.create('http://uca.edu')
        >>> url.svg(sys.stdout, scale=1)
        >>> url.svg('uca.svg', scale=4)
        >>> number = pyqrcode.create(123456789012345)
        >>> number.png('big-number.png')
"""
from __future__ import absolute_import, unicode_literals
from . import builder, tables
try:
    str = unicode  # Python 2
except NameError:
    pass


def create(content, error='H', version=None, mode=None, encoding=None):
    """When creating a QR code only the content to be encoded is required,
    all the other properties of the code will be guessed based on the
    contents given. This function will return a :class:`QRCode` object.

    Unless you are familiar with QR code's inner workings
    it is recommended that you just specify the content and nothing else.
    However, there are cases where you may want to specify the various
    properties of the created code manually, this is what the other
    parameters do. Below, you will find a lengthy explanation of what
    each parameter is for. Note, the parameter names and values are taken
    directly from the standards. You may need to familiarize yourself
    with the terminology of QR codes for the names to make sense.

    The *error* parameter sets the error correction level of the code. There
    are four levels defined by the standard. The first is level 'L' which
    allows for 7% of the code to be corrected. Second, is level 'M' which
    allows for 15% of the code to be corrected. Next, is level 'Q' which
    is the most common choice for error correction, it allow 25% of the
    code to be corrected. Finally, there is the highest level 'H' which
    allows for 30% of the code to be corrected. There are several ways to
    specify this parameter, you can use an upper or lower case letter,
    a float corresponding to the percentage of correction, or a string
    containing the percentage. See tables.modes for all the possible
    values. By default this parameter is set to 'H' which is the highest
    possible error correction, but it has the smallest available data
    capacity.

    The *version* parameter specifies the size and data capacity of the
    code. Versions are any integer between 1 and 40. Where version 1 is
    the smallest QR code, and version 40 is the largest. If this parameter
    is left unspecified, then the contents and error correction level will
    be used to guess the smallest possible QR code version that the
    content will fit inside of. You may want to specify this parameter
    for consistency when generating several QR codes with varying amounts
    of data. That way all of the generated codes would have the same size.

    The *mode* parameter specifies how the contents will be encoded. By
    default, the best possible encoding for the contents is guessed. There
    are four possible encoding methods. First, is 'numeric' which is
    used to encode integer numbers. Next, is 'alphanumeric' which is
    used to encode some ASCII characters. This mode uses only a limited
    set of characters. Most problematic is that it can only use upper case
    English characters. See `tables.ascii_codes` for
    a complete list of available characters. We then have 'binary' encoding
    which just encodes the bytes directly into the QR code (this encoding
    is the least efficient). Finally, there is 'kanji'  encoding (i.e.
    Japanese characters), this encoding is unimplemented at this time.

    The *encoding* parameter specifies how the content will be encoded if
    the mode is ``'binary'``. Valid values are ``ISO-8859-1`` (default and
    standard-conform) or ``UTF-8`` (not standard-conform but supported by
    most QR code readers. If encoding is set to ``None`` (default), the
    implementation uses an appropriate encoding automatically.
    """
    return QRCode(content, error, version, mode, encoding)


class QRCode:
    """This class represents a QR code. To use this class simply give the
    constructor a string representing the data to be encoded, it will then
    build a code in memory. You can then save it in various formats. Note,
    codes can be written out as PNG files but this requires the PyPNG module.
    You can find the PyPNG module at http://packages.python.org/pypng/.

    Examples:
        >>> from pyqrcode import QRCode
        >>> import sys
        >>> url = QRCode('http://uca.edu')
        >>> url.svg(sys.stdout, scale=1)
        >>> url.svg('uca.svg', scale=4)
        >>> number = QRCode(123456789012345)
        >>> number.png('big-number.png')

    .. note::
        For what all of the parameters do, see the :func:`pyqrcode.create`
        function.
    """
    def __init__(self, content, error='H', version=None, mode=None, encoding=None):
        if encoding is not None \
                and encoding.lower() not in ('utf-8', 'iso-8859-1', 'latin1',
                                             'latin'):
            raise ValueError('Unsupported encoding "{0}". '
                             'Supported: "UTF-8" and "ISO-8859-1".'
                             .format(encoding))

        self.data = str(content)

        # Check that the passed in error level is valid
        try:
            self.error = tables.error_level[str(error).upper()]
        except KeyError:
            raise ValueError('The error parameter is not one of '
                             '"L", "M", "Q", or "H.", got "{0}"'.format(error))

        # Guess the mode of the code, this will also be used for error checking
        guessed_content_type = self._detect_content_type()

        # Force a passed in mode to be lowercase
        if mode is not None:
            mode = mode.lower()
            if mode not in tables.modes or mode == 'kanji':
                raise ValueError('Unsupported mode "{0}". '
                                 'Supported: "numeric", "alphanumeric", "binary"'
                                 .format(mode))

        # Check that the mode parameter is compatible with the contents
        if not mode:
            # Use the guessed mode
            self.mode = guessed_content_type
            self.mode_num = tables.modes[self.mode]
        elif guessed_content_type == 'binary' and \
             tables.modes[mode] != tables.modes['binary']:
            # Binary is only guessed as a last resort, if the
            # passed in mode is not binary the data won't encode
            raise ValueError('The content provided cannot be encoded with '
                             'the mode {0}, it can only be encoded as '
                             'binary.'.format(mode))
        elif tables.modes[mode] == tables.modes['numeric'] and \
             guessed_content_type != 'numeric':
            # If numeric encoding is requested make sure the data can
            # be encoded in that format
            raise ValueError('The content cannot be encoded as numeric.')
        else:
            # The data should encode with the passed in mode
            self.mode = mode
            self.mode_num = tables.modes[self.mode]

        encoded_data = self.data
        if isinstance(encoded_data, bytes):
            encoded_data = encoded_data.decode('utf-8')
        if self.mode == 'binary':
            if encoding is not None:
                encoded_data = encoded_data.encode(encoding)
            else:
                # Try to use standard-conform encoding
                try:
                    encoded_data = encoded_data.encode('iso-8859-1')
                except UnicodeError:
                    encoded_data = encoded_data.encode('utf-8')

        # Guess the "best" version
        self.version = self._pick_best_fit(encoded_data)

        # If the user supplied a version, then check that it has
        # sufficient data capacity for the contents passed in
        if version is not None:
            if version >= self.version:
                self.version = version
            else:
                raise ValueError('The data will not fit inside a version {0} '
                                 'code with the given encoding and error '
                                 'level (the code must be at least a '
                                 'version {1}).'.format(version, self.version))
        # Build the QR code
        self.builder = builder.QRCodeBuilder(data=encoded_data,
                                             version=self.version,
                                             mode=self.mode,
                                             error=self.error)
        # Save the code for easier reference
        self.code = self.builder.code

    def __str__(self):
        return repr(self)

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return "QRCode(content='{0}', error='{1}', version={2}, mode='{3}')" \
                .format(self.data, self.error, self.version, self.mode)

    def _detect_content_type(self):
        """This method tries to auto-detect the type of the data. It first
        tries to see if the data is a valid integer, in which case it returns
        numeric. Next, it tests the data to see if it is 'alphanumeric.' QR
        Codes use a special table with very limited range of ASCII characters.
        The code's data is tested to make sure it fits inside this limited
        range. If all else fails, the data is determined to be of type
        'binary.'

        Note, encoding 'kanji' is not yet implemented.
        """
        # See if data represents a number
        if self.data.isdigit():
            return 'numeric'
        # See if that data is alphanumeric based on the standards
        # special ASCII table
        valid_characters = tables.ascii_codes.keys()
        if all(map(lambda x: x in valid_characters, self.data)):
            return 'alphanumeric'
        # All of the tests failed. The content can only be binary.
        return 'binary'

    def _pick_best_fit(self, encoded_data):
        """This method return the smallest possible QR code version number
        that will fit the specified data with the given error level.
        """
        data_len = len(encoded_data)
        for version in range(1, 41):
            # Get the maximum possible capacity
            capacity = tables.data_capacity[version][self.error][self.mode_num]
            # Check the capacity
            if capacity >= data_len:
                return version
        raise ValueError('The data will not fit in any QR code version '
                         'with the given encoding and error level.')

    def get_png_size(self, scale=1, border=4):
        """This is method helps users determine what *scale* to use when
        creating a PNG of this QR code. It is meant mostly to be used in the
        console to help the user determine the pixel size of the code
        using various scales.

        This method will return an integer representing the width and height of
        the QR code in pixels, as if it was drawn using the given *scale*.
        Because QR codes are square, the number represents both dimensions.

        :param scale: The scale to use (default: 1).
        :param border: The border around the actual QR code (default: 4)

        Example:
            >>> code = pyqrcode.QRCode("I don't like spam!")
            >>> print(code.get_png_size(1))
            31
            >>> print(code.get_png_size(5))
            155
        """
        return builder._get_png_size(self.version, int(scale), border)

    def png(self, file, scale=1, module_color=(0, 0, 0, 255),
            background=(255, 255, 255, 255), border=4, debug=False):
        """This method writes the QR code out as an PNG image. The resulting
        PNG has a bit depth of 1 (or 2 if in debug is enabled).
        The file parameter is used to specify where
        to write the image to. It can either be a writable (binary) stream
        or a file path.

        .. note::
            This method depends on the pypng module to actually create the
            PNG file.

        This method will write the given *file* out as a PNG file. The file
        can be either a string file path, or a writable stream.

        The *scale* parameter sets how large to draw a single module. By
        default one pixel is used to draw a single module. This may make the
        code too small to be read efficiently. Increasing the scale will make
        the code larger. Only integer scales are usable. This method will
        attempt to coerce the parameter into an integer (e.g. 2.5 will become 2,
        and '3' will become 3).

        The *module_color* parameter sets what color to use for the encoded
        modules (the black part on most QR codes). The *background* parameter
        sets what color to use for the background (the white part on most
        QR codes). Colors should be specified as either
        a list or a tuple of length 3 or 4 or as string representing a
        hexadecimal color. If the color is a tuple or a list, the components of
        the list must be integers between 0 and 255. The first three member
        give the RGB color. The fourth member gives the alpha component, where
        0 is transparent and 255 is opaque.
        Note, many color combinations are unreadable by scanners, so be careful.

        :param module_color: Color of the QR code
                (default: ``(0, 0, 0, 255)`` (black))
        :param background: Optional background color. If set to ``None`` the PNG
                will have a transparent background.
                (default: ``(255, 255, 255, 255)`` (white))
        :param border: Border around the QR code (also known as quiet zone)
                (default: ``4``). Set to zero (``0``) if the code shouldn't
                have a border.
        :param debug: Inidicates if errors in the QR code should be added (as
                red modules) to the output (default: ``False``).

        Example:
            >>> code = pyqrcode.create('Are you suggesting coconuts migrate?')
            >>> code.png('swallow.png', scale=5)
            >>> code.png('swallow.png', scale=5,
                         module_color=(0x66, 0x33, 0x0),      #Dark brown
                         background=(0xff, 0xff, 0xff, 0x88)) #50% transparent white
            >>> code.png('swallow.png', scale=5, module_color='#06c', # A kind of blue
                         background=None)
        """
        builder._png(self.code, self.version, file, scale,
                     module_color, background, border, debug)

    def svg(self, file, scale=1, module_color='#000', background=None,
            border=4, xmldecl=True, svgns=True, title=None, svgclass='pyqrcode',
            lineclass='pyqrline', omithw=False, debug=False):
        """This method writes the QR code out as an SVG document. The
        code is drawn by drawing only the modules corresponding to a 1. They
        are drawn using a line, such that contiguous modules in a row
        are drawn with a single line.

        The *file* parameter is used to specify where to write the document
        to. It can either be a writable (binary) stream or a file path.

        The *scale* parameter sets how large to draw
        a single module. By default one pixel is used to draw a single
        module. This may make the code too small to be read efficiently.
        Increasing the scale will make the code larger. Unlike the png() method,
        this method will accept fractional scales (e.g. 2.5).

        Note, three things are done to make the code more appropriate for
        embedding in a HTML document. The "white" part of the code is actually
        transparent. The code itself has a class of "pyqrcode". The lines
        making up the QR code have a class "pyqrline". These should make the
        code easier to style using CSS.

        You can also set the colors directly using the *module_color* and
        *background* parameters. The *module_color* parameter sets what color to
        use for the data modules (the black part on most QR codes). The
        *background* parameter sets what color to use for the background (the
        white part on most QR codes). The parameters can be set to any valid
        SVG or HTML color. If the background is set to None, then no background
        will be drawn, i.e. the background will be transparent. Note, many color
        combinations are unreadable by scanners, so be careful.

        :param module_color: Color of the QR code (default: ``#000`` (black))
        :param background: Optional background color.
                (default: ``None`` (no background))
        :param border: Border around the QR code (also known as  quiet zone)
                (default: ``4``). Set to zero (``0``) if the code shouldn't
                have a border.
        :param xmldecl: Inidcates if the XML declaration header should be
                written (default: ``True``)
        :param svgns: Indicates if the SVG namespace should be written
                (default: ``True``)
        :param title: Optional title of the generated SVG document.
        :param svgclass: The CSS class of the SVG document
                (if set to ``None``, the SVG element won't have a class).
        :param lineclass: The CSS class of the path element
                (if set to ``None``, the path won't have a class).
        :param omithw: Indicates if width and height attributes should be
                omitted (default: ``False``). If these attributes are omitted,
                a ``viewBox`` attribute will be added to the document.
        :param debug: Inidicates if errors in the QR code should be added to the
                output (default: ``False``).

        Example:
            >>> code = pyqrcode.create('Hello. Uhh, can we have your liver?')
            >>> code.svg('live-organ-transplants.svg', 3.6)
            >>> code.svg('live-organ-transplants.svg', scale=4,
                         module_color='brown', background='0xFFFFFF')
        """
        builder._svg(self.code, self.version, file, scale,
                     module_color, background, border, xmldecl, svgns, title,
                     svgclass, lineclass, omithw, debug)

    def eps(self, file, scale=1, module_color=(0, 0, 0), background=None,
            border=4):
        """This method writes the QR code out as an EPS document. The
        code is drawn by drawing only the modules corresponding to a 1. They
        are drawn using a line, such that contiguous modules in a row
        are drawn with a single line. The file parameter is used to
        specify where to write the document to. It can either be a writable
        (text) stream or a file path. The scale parameter is sets how large
        to draw a single module. By default one point (1/72 inch) is used to
        draw a single module. This may make the code to small to be read
        efficiently.
        Increasing the scale will make the code larger. This method will accept
        fractional scales (e.g. 2.5).

        :param module_color: Color of the QR code (default: ``(0, 0, 0)`` (black))
                The color can be specified as triple of floats (range: 0 .. 1)
                or triple of integers (range: 0 .. 255) or as hexadecimal value
                (i.e. ``#36c`` or ``#33B200``).
        :param background: Optional background color.
                (default: ``None`` (no background)). See `module_color` for the
                supported values.
        :param border: Border around the QR code (also known as  quiet zone)
                (default: ``4``). Set to zero (``0``) if the code shouldn't
                have a border.

        Examples:
            >>> qr = pyqrcode.create('Hello world')
            >>> qr.eps('hello-world.eps', scale=2.5, module_color='#36C')
            >>> qr.eps('hello-world2.eps', background='#eee')
            >>> out = io.StringIO()
            >>> qr.eps(out, module_color=(.4, .4, .4))
        """
        builder._eps(self.code, self.version, file, scale, module_color,
                     background, border)

    def terminal(self, module_color='default', background='reverse'):
        """This method returns a string containing ASCII escape codes,
        such that if printed to a compatible terminal, it will display
        a vaild QR code. The code is printed using ASCII escape
        codes that alter the coloring of the background.

        The *module_color* parameter sets what color to
        use for the data modules (the black part on most QR codes).
        Likewise, the *background* parameter sets what color to use
        for the background (the white part on most QR codes).  

        There are two options for colors. The first, and most widely
        supported, is to use the 8 or 16 color scheme. This scheme uses
        eight to sixteen named colors. The following colors are
        supported the most widely supported: black, red, green,
        yellow, blue, magenta, and cyan. There are an some additional
        named colors that are supported by most termials: light gray,
        dark gray, light red, light green, light blue, light yellow,
        light magenta, light cyan, and white. 

        There are two special named colors. The first is the
        "default" color. This color is the color the background of
        the terminal is set to. The next color is the "reverse"
        color. This is not really a color at all but a special
        property that will reverse the current color. These two colors
        are the default values for *module_color* and *background*
        respectively. These values should work on most terminals.

        Finally, there is one more way to specify the color. Some
        terminals support 256 colors. The actual colors displayed in the
        terminal is system dependent. This is the least transportable option.
        To use the 256 color scheme set *module_color* and/or
        *background* to a number between 0 and 256.

        Example:
            >>> code = pyqrcode.create('Example')
            >>> text = code.terminal()
            >>> print(text)
        """
        return builder._terminal(self.code, module_color, background)

    def text(self, module_color='1', background='0', border=4, debug=True):
        """This method returns a string based representation of the QR code.
        The data modules are represented by 1's and the background modules are
        represented by 0's. The main purpose of this method is to allow a user
        to write their own renderer.

        :param module_color: The character to use for the QR code modules
                (default: "1")
        :param background: The character to use for the QR code background
                (default: "0").
        :param border: Border around the QR code (also known as quiet zone)
                (default: ``4``). Set to zero (``0``) if the code shouldn't
                have a border.
        :param debug: Inidicates if errors in the QR code should be added (as
                empty space modules) to the output (default: ``True``).
                Note, that errors will be invisible if background is set to
                ``' '``.

        Example:
            >>> code = pyqrcode.create('Example')
            >>> text = code.text()
            >>> print(text)
        """
        return builder._text(self.code, module_color, background, border, debug)
