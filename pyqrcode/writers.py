# -*- coding: utf-8 -*-
#
# Copyright (c) 2013, Michael Nooner
# Copyright (c) 2018 -- Lars Heuer - Semagia <http://www.semagia.com/>.
# All rights reserved.
#
# License: BSD License
#
"""\
Standard serializers and utility functions for serializers.

This module does not belong to the public API.
"""
from __future__ import absolute_import, unicode_literals, with_statement
import io
import math
import codecs
import base64
from pyqrcode.builder import _get_symbol_size
from contextlib import contextmanager
_PY2 = False
try:  # pragma: no cover
    from itertools import zip_longest
except ImportError:  # pragma: no cover
    _PY2 = True
    from itertools import izip_longest as zip_longest
    range = xrange
    str = unicode
    from io import open


@contextmanager
def _writable(file_or_path, mode, encoding=None):
    """\
    Returns a writable file-like object.

    Usage::

        with writable(file_name_or_path, 'wb') as f:
            ...


    :param file_or_path: Either a file-like object or a filename.
    :param str mode: String indicating the writing mode (i.e. ``'wb'``)
    """
    f = file_or_path
    must_close = False
    try:
        file_or_path.write
        if encoding is not None:
            f = codecs.getwriter(encoding)(file_or_path)
    except AttributeError:
        f = open(file_or_path, mode, encoding=encoding)
        must_close = True
    try:
        yield f
    finally:
        if must_close:
            f.close()


#: This is a table of ASCII escape code for terminal colors. QR codes
#: are drawn using a space with a colored background. Hence, only
#: codes affecting background colors have been added.
#: http://misc.flogisoft.com/bash/tip_colors_and_formatting
_TERM_COLORS = {
    'default': 49,
    'background': 49,

    'reverse': 7,
    'reversed': 7,
    'inverse': 7,
    'inverted': 7,

    'black': 40,
    'red': 41,
    'green': 42,
    'yellow': 43,
    'blue': 44,
    'magenta': 45,
    'cyan': 46,
    'light gray': 47,
    'light grey': 47,
    'dark gray': 100,
    'dark grey': 100,
    'light red': 101,
    'light green': 102,
    'light blue': 103,
    'light yellow': 104,
    'light magenta': 105,
    'light cyan': 106,
    'white': 107
}


def write_terminal(code, module_color='default', background='reverse', quiet_zone=4):
    """This method returns a string containing ASCII escape codes,
    such that if printed to a terminal, it will display a vaild
    QR code. The module_color and the background color should be keys
    in the tables.term_colors table for printing using the 8/16
    color scheme. Alternatively, they can be a number between 0 and
    256 in order to use the 88/256 color scheme. Otherwise, a
    ValueError will be raised.

    Note, the code is outputted by changing the background color. Then
    two spaces are written to the terminal. Finally, the terminal is
    reset back to how it was.
    """
    buf = io.StringIO()

    def draw_border():
        for i in range(quiet_zone):
            buf.write(background)

    if module_color in _TERM_COLORS:
        data = '\033[{0}m  \033[0m'.format(
            _TERM_COLORS[module_color])
    elif 0 <= module_color <= 256:
        data = '\033[48;5;{0}m  \033[0m'.format(module_color)
    else:
        raise ValueError('The module color, {0}, must a key in '
                         'pyqrcode.tables.term_colors or a number '
                         'between 0 and 256.'.format(
                         module_color))

    if background in _TERM_COLORS:
        background = '\033[{0}m  \033[0m'.format(
            _TERM_COLORS[background])
    elif 0 <= background <= 256:
        background = '\033[48;5;{0}m  \033[0m'.format(background)
    else:
        raise ValueError('The background color, {0}, must a key in '
                         'pyqrcode.tables.term_colors or a number '
                         'between 0 and 256.'.format(
                         background))

    # This will be the beginning and ending row for the code.
    border_row = background * (len(code[0]) + (2 * quiet_zone))
    # Make sure we begin on a new line, and force the terminal back
    # to normal
    buf.write('\n')
    # QRCodes have a quiet zone consisting of background modules
    for i in range(quiet_zone):
        buf.write(border_row)
        buf.write('\n')
    for row in code:
        # Each code has a quiet zone on the left side, this is the left
        # border for this code
        draw_border()
        for bit in row:
            if bit == 1:
                buf.write(data)
            elif bit == 0:
                buf.write(background)
        # Each row ends with a quiet zone on the right side, this is the
        # right hand border background modules
        draw_border()
        buf.write('\n')
    # QRCodes have a background quiet zone row following the code
    for i in range(quiet_zone):
        buf.write(border_row)
        buf.write('\n')
    return buf.getvalue()


def write_text(code, quiet_zone=4):
    """This method returns a text based representation of the QR code.
    This is useful for debugging purposes.
    """
    buf = io.StringIO()
    border_row = '0' * (len(code[0]) + (quiet_zone*2))
    # Every QR code start with a quiet zone at the top
    for b in range(quiet_zone):
        buf.write(border_row)
        buf.write('\n')
    for row in code:
        # Draw the starting quiet zone
        for b in range(quiet_zone):
            buf.write('0')
        # Actually draw the QR code
        for bit in row:
            if bit == 1:
                buf.write('1')
            elif bit == 0:
                buf.write('0')
            # This is for debugging unfinished QR codes,
            # unset pixels will be spaces.
            else:
                buf.write(' ')
        # Draw the ending quiet zone
        for b in range(quiet_zone):
            buf.write('0')
        buf.write('\n')
    # Every QR code ends with a quiet zone at the bottom
    for b in range(quiet_zone):
        buf.write(border_row)
        buf.write('\n')
    return buf.getvalue()


def write_xbm(code, scale=1, quiet_zone=4):
    """This function will format the QR code as a X BitMap.
    This can be used to display the QR code with Tkinter.
    """
    buf = io.StringIO()
    # Calculate the width in pixels
    pixel_width = (len(code[0]) + quiet_zone * 2) * scale
    # Add the size information and open the pixel data section
    buf.write('#define im_width ')
    buf.write(str(pixel_width))
    buf.write('\n')
    buf.write('#define im_height ')
    buf.write(str(pixel_width))
    buf.write('\n')
    buf.write('static char im_bits[] = {\n')
    # Calculate the number of bytes per row
    byte_width = int(math.ceil(pixel_width / 8.0))
    # Add the top quiet zone
    buf.write(('0x00,' * byte_width + '\n') * quiet_zone * scale)
    for row in code:
        # Add the left quiet zone
        row_bits = '0' * quiet_zone * scale
        # Add the actual QR code
        for pixel in row:
            row_bits += str(pixel) * scale
        # Add the right quiet zone
        row_bits += '0' * quiet_zone * scale
        # Format the row
        formated_row = ''
        for b in range(byte_width):
            formated_row += '0x{0:02x},'.format(int(row_bits[:8][::-1], 2))
            row_bits = row_bits[8:]
        formated_row += '\n'
        # Add the formatted row
        buf.write(formated_row * scale)
    # Add the bottom quiet zone and close the pixel data section
    buf.write(('0x00,' * byte_width + '\n') * quiet_zone * scale)
    buf.write('};')
    return buf.getvalue()


def write_svg(code, version, file, scale=1, module_color='#000', background=None,
              quiet_zone=4, xmldecl=True, svgns=True, title=None, svgclass='pyqrcode',
              lineclass='pyqrline', omithw=False, debug=False):
    """This function writes the QR code out as an SVG document. The
    code is drawn by drawing only the modules corresponding to a 1. They
    are drawn using a line, such that contiguous modules in a row
    are drawn with a single line. The file parameter is used to
    specify where to write the document to. It can either be a writable (binary)
    stream or a file path. The scale parameter is sets how large to draw
    a single module. By default one pixel is used to draw a single
    module. This may make the code to small to be read efficiently.
    Increasing the scale will make the code larger. This method will accept
    fractional scales (e.g. 2.5).

    :param module_color: Color of the QR code (default: ``#000`` (black))
    :param background: Optional background color.
            (default: ``None`` (no background))
    :param quiet_zone: Border around the QR code (also known as  quiet zone)
            (default: ``4``). Set to zero (``0``) if the code shouldn't
            have a border.
    :param xmldecl: Inidcates if the XML declaration header should be written
            (default: ``True``)
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
    """
    from functools import partial
    from xml.sax.saxutils import quoteattr

    def write_unicode(write_meth, unicode_str):
        """\
        Encodes the provided string into UTF-8 and writes the result using
        the `write_meth`.
        """
        write_meth(unicode_str.encode('utf-8'))

    def line(x, y, length, relative):
        """Returns coordinates to draw a line with the provided length.
        """
        return '{0}{1} {2}h{3}'.format(('m' if relative else 'M'), x, y, length)

    def errline(col_number, row_number):
        """Returns the coordinates to draw an error bit.
        """
        # Debug path uses always absolute coordinates
        # .5 == stroke / 2
        return line(col_number + quiet_zone, row_number + quiet_zone + .5, 1, False)

    width, height = _get_symbol_size(version, scale, quiet_zone)
    with _writable(file, 'wb') as f:
        write = partial(write_unicode, f.write)
        write_bytes = f.write
        # Write the document header
        if xmldecl:
            write_bytes(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        write_bytes(b'<svg')
        if svgns:
            write_bytes(b' xmlns="http://www.w3.org/2000/svg"')
        if not omithw:
            write(' width="{0}" height="{1}"'.format(width, height))
        else:
            write(' viewBox="0 0 {0} {1}"'.format(width, height))
        if svgclass is not None:
            write_bytes(b' class=')
            write(quoteattr(svgclass))
        write_bytes(b'>')
        if title is not None:
            write('<title>{0}</title>'.format(title))
        # Draw a background rectangle if necessary
        if background is not None:
            write('<path fill="{2}" d="M0 0h{0}v{1}h-{0}z"/>'
                    .format(width, height, background))
        write_bytes(b'<path')
        if scale != 1:
            write(' transform="scale({0})"'.format(scale))
        if module_color is not None:
            write_bytes(b' stroke=')
            write(quoteattr(module_color))
        if lineclass is not None:
            write_bytes(b' class=')
            write(quoteattr(lineclass))
        write_bytes(b' d="')
        # Used to keep track of unknown/error coordinates.
        debug_path = ''
        # Current pen pointer position
        x, y = -quiet_zone, quiet_zone - .5  # .5 == stroke-width / 2
        wrote_bit = False
        # Loop through each row of the code
        for rnumber, row in enumerate(code):
            start_column = 0  # Reset the starting column number
            coord = ''  # Reset row coordinates
            y += 1  # Pen position on y-axis
            length = 0  # Reset line length
            # Examine every bit in the row
            for colnumber, bit in enumerate(row):
                if bit == 1:
                    length += 1
                else:
                    if length:
                        x = start_column - x
                        coord += line(x, y, length, relative=wrote_bit)
                        x = start_column + length
                        y = 0  # y-axis won't change unless the row changes
                        length = 0
                        wrote_bit = True
                    start_column = colnumber + 1
                    if debug and bit != 0:
                        debug_path += errline(colnumber, rnumber)
            if length:
                x = start_column - x
                coord += line(x, y, length, relative=wrote_bit)
                x = start_column + length
                wrote_bit = True
            write(coord)
        # Close path
        write_bytes(b'"/>')
        if debug and debug_path:
            write_bytes(b'<path')
            if scale != 1:
                write(' transform="scale({0})"'.format(scale))
            write(' class="pyqrerr" stroke="red" d="{0}"/>'.format(debug_path))
        # Close document
        write_bytes(b'</svg>\n')


def write_eps(code, version, file_or_path, scale=1, module_color=(0, 0, 0),
              background=None, quiet_zone=4):
    """This function writes the QR code out as an EPS document. The
    code is drawn by drawing only the modules corresponding to a 1. They
    are drawn using a line, such that contiguous modules in a row
    are drawn with a single line. The file parameter is used to
    specify where to write the document to. It can either be a writable (text)
    stream or a file path. The scale parameter is sets how large to draw
    a single module. By default one point (1/72 inch) is used to draw a single
    module. This may make the code to small to be read efficiently.
    Increasing the scale will make the code larger. This function will accept
    fractional scales (e.g. 2.5).

    :param module_color: Color of the QR code (default: ``(0, 0, 0)`` (black))
            The color can be specified as triple of floats (range: 0 .. 1) or
            triple of integers (range: 0 .. 255) or as hexadecimal value (i.e.
            ``#36c`` or ``#33B200``).
    :param background: Optional background color.
            (default: ``None`` (no background)). See `module_color` for the
            supported values.
    :param quiet_zone: Border around the QR code (also known as  quiet zone)
            (default: ``4``). Set to zero (``0``) if the code shouldn't
            have a border.
    """
    from functools import partial
    import time
    import textwrap

    def write_line(writemeth, content):
        """\
        Writes `content` and ``LF``.
        """
        # Postscript: Max. 255 characters per line
        for line in textwrap.wrap(content, 255):
            writemeth(line)
            writemeth('\n')

    def line(offset, length):
        """\
        Returns coordinates to draw a line with the provided length.
        """
        res = ''
        if offset > 0:
            res = ' {0} 0 m'.format(offset)
        res += ' {0} 0 l'.format(length)
        return res

    def rgb_to_floats(color):
        """\
        Converts the provided color into an acceptable format for Postscript's
         ``setrgbcolor``
        """
        def to_float(clr):
            if isinstance(clr, float):
                if not 0.0 <= clr <= 1.0:
                    raise ValueError('Invalid color "{0}". Not in range 0 .. 1'
                                     .format(clr))
                return clr
            if not 0 <= clr <= 255:
                raise ValueError('Invalid color "{0}". Not in range 0 .. 255'
                                 .format(clr))
            return 1/255.0 * clr if clr != 1 else clr

        if not isinstance(color, (tuple, list)):
            color = _hex_to_rgb(color)
        return tuple([to_float(i) for i in color])

    width, height = _get_symbol_size(version, scale, quiet_zone)
    with _writable(file_or_path, 'w') as f:
        writeline = partial(write_line, f.write)
        # Write common header
        writeline('%!PS-Adobe-3.0 EPSF-3.0')
        writeline('%%Creator: PyQRCode <https://pypi.python.org/pypi/PyQRCode/>')
        writeline('%%CreationDate: {0}'.format(time.strftime("%Y-%m-%d %H:%M:%S")))
        writeline('%%DocumentData: Clean7Bit')
        writeline('%%BoundingBox: 0 0 {0} {1}'.format(width, height))
        # Write the shortcuts
        writeline('/M { moveto } bind def')
        writeline('/m { rmoveto } bind def')
        writeline('/l { rlineto } bind def')
        mod_color = module_color if module_color == (0, 0, 0) else rgb_to_floats(module_color)
        if background is not None:
            writeline('{0:f} {1:f} {2:f} setrgbcolor clippath fill'
                      .format(*rgb_to_floats(background)))
            if mod_color == (0, 0, 0):
                # Reset RGB color back to black iff module color is black
                # In case module color != black set the module RGB color later
                writeline('0 0 0 setrgbcolor')
        if mod_color != (0, 0, 0):
            writeline('{0:f} {1:f} {2:f} setrgbcolor'.format(*mod_color))
        if scale != 1:
            writeline('{0} {0} scale'.format(scale))
        writeline('newpath')
        # Current pen position y-axis
        # Note: 0, 0 = lower left corner in PS coordinate system
        y = _get_symbol_size(version, scale=1, quiet_zone=0)[1] + quiet_zone - .5  # .5 = linewidth / 2
        last_bit = 1
        # Loop through each row of the code
        for row in code:
            offset = 0  # Set x-offset of the pen
            length = 0
            y -= 1  # Move pen along y-axis
            coord = '{0} {1} M'.format(quiet_zone, y)  # Move pen to initial pos
            for bit in row:
                if bit != last_bit:
                    if length:
                        coord += line(offset, length)
                        offset = 0
                        length = 0
                    last_bit = bit
                if bit == 1:
                    length += 1
                else:
                    offset += 1
            if length:
                coord += line(offset, length)
            writeline(coord)
        writeline('stroke')
        writeline('%%EOF')


def _hex_to_rgb(color):
    """\
    Helper function to convert a color provided in hexadecimal format
    as RGB triple.
    """
    if color[0] == '#':
        color = color[1:]
    if len(color) == 3:
        color = color[0] * 2 + color[1] * 2 + color[2] * 2
    if len(color) != 6:
        raise ValueError('Input #{0} is not in #RRGGBB format'.format(color))
    return [int(n, 16) for n in (color[:2], color[2:4], color[4:])]
