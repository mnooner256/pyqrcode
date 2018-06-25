#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 -- Lars Heuer - Semagia <http://www.semagia.com/>.
# All rights reserved.
#
# License: BSD License
#
"""\
Command line script to generate QR Codes with Segno.

"QR Code" and "Micro QR Code" are registered trademarks of DENSO WAVE INCORPORATED.
"""
from __future__ import absolute_import, unicode_literals
import os
import sys
import argparse
import pyqrcode


_SUPPORTED_EXT = ('svg', 'png', 'eps')
_COMMON_ARGS = ('version', 'error', 'mode', 'scale', 'quiet_zone',
                'module_color', 'background')


def make_parser():
    """\
    Returns the command line parser.
    """

    def _convert_scale(val):
        val = float(val)
        return val if val != int(val) else int(val)

    parser = argparse.ArgumentParser(prog='pyqr',
                                     description='PyQRCode QR Code generator version {0}'.format(pyqrcode.__version__))
    parser.add_argument('--version', '-v', help='QR Code version: 1 .. 40',
                        required=False,)
    parser.add_argument('--error', '-e', help='Error correction level: "L": 7%%, "M": 15%%, "Q": 25%%, "H": 30%% (default)',
                        choices=('L', 'M', 'Q', 'H'),
                        default='H',
                        type=lambda x: x.upper())
    parser.add_argument('--mode', '-m', help='Mode',
                        choices=('numeric', 'alphanumeric', 'byte', 'kanji'),
                        default=None,
                        type=lambda x: x.lower())
    parser.add_argument('--scale', '-s', help='Scaling factor',
                        default=1,
                        type=_convert_scale)
    parser.add_argument('--quietzone', '-qz', help='Size of the quiet zone',
                        dest='quiet_zone',
                        default=4,
                        type=int)
    parser.add_argument('--color', help='Color of the dark modules. Use "transparent" to set the color to None (not supported by all serializers)',
                        dest='module_color')
    parser.add_argument('--background', help='Color of the light modules. Use "transparent" to set the background to None (not supported by all serializers)')
    parser.add_argument('--output', '-o', help='Output file. If not specified, the QR Code is printed to the terminal',
                        required=False,
                        )
    # SVG
    svg_group = parser.add_argument_group('SVG', 'SVG specific options')
    svg_group.add_argument('--no-classes', help='Omits the (default) SVG classes',
                           action='store_true')
    svg_group.add_argument('--no-xmldecl', help='Omits the XML declaration header',
                           dest='xmldecl',
                           action='store_false')
    svg_group.add_argument('--no-namespace', help='Indicates that the SVG document should have no SVG namespace declaration',
                           dest='svgns',
                           action='store_false')
    svg_group.add_argument('--title', help='Specifies the title of the SVG document')
    svg_group.add_argument('--svgclass', help='Indicates the CSS class of the <svg/> element')
    svg_group.add_argument('--lineclass', help='Indicates the CSS class of the <path/> element (the dark modules)')
    svg_group.add_argument('--no-size', help='Indicates that the SVG document should not have "width" and "height" attributes',
                           dest='omithw',
                           action='store_true')
    parser.add_mutually_exclusive_group().add_argument('--ver', '-V', help="Shows PyQRCode's version",
                                                       action='version',
                                                       version='PyQRCode {0}'.format(pyqrcode.__version__))
    parser.add_argument('content', nargs='+', help='The content to encode')
    return parser


def parse(args):
    """\
    Parses the arguments and returns the result.
    """
    parser = make_parser()
    if not len(args):
        parser.print_help()
        sys.exit(1)
    parsed_args = parser.parse_args(args)
    return _AttrDict(vars(parsed_args))


def build_config(config, output=None):
    """\
    Builds a configuration and returns it. The config contains only keywords,
    which are supported by the serializer. Unsupported values are ignored.
    """
    # Done here since it seems not to be possible to detect if an argument
    # was supplied by the user or if it's the default argument.
    # If using type=lambda v: None if v in ('transparent', 'trans') else v
    # we cannot detect if "None" comes from "transparent" or the default value
    for clr in ('module_color', 'background'):
        val = config.pop(clr, None)
        if val in ('transparent', 'trans'):
            config[clr] = None
        elif val:
            config[clr] = val
    for name in ('svgclass', 'lineclass'):
        if config.get(name, None) is None:
            config.pop(name, None)
    if config.pop('no_classes', False):
        config['svgclass'] = None
        config['lineclass'] = None
    ext = output[output.rfind('.') + 1:].lower() if output is not None else None
    if ext is not None and ext != 'svg':
        # Drop unsupported arguments from config rather than getting a
        # "unsupported keyword" exception
        for k in list(config):
            if k not in _COMMON_ARGS:
                del config[k]

    return config


def make_code(config):
    mode = config.pop('mode')
    if mode == 'byte':
        mode = 'binary'
    version = config.pop('version')
    if version:
        version = int(version)
    kw = dict(mode=mode, error=config.pop('error'), version=version)
    return pyqrcode.create(' '.join(config.pop('content')), **kw)


def main(args=sys.argv[1:]):

    def error_msg(msg):
        sys.stderr.writelines([msg, os.linesep])
        return sys.exit(1)

    config = parse(args)
    output = config.pop('output')
    ext = None
    if output is not None:
        ext = output[output.rfind('.') + 1:].lower()
        if ext not in _SUPPORTED_EXT:
            return error_msg('Unsupported output format "{}"'.format(ext.upper()))
    try:
        qr = make_code(config)
    except ValueError as ex:
        return error_msg(str(ex))
    try:
        if output is None:
            _write_to_terminal(qr, quiet_zone=config['quiet_zone'])
        else:
            meth = getattr(qr, ext)
            meth(output, **build_config(config, output))
    except ValueError as ex:
        return error_msg(str(ex))
    return 0


class _AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(_AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def _write_to_terminal(qrcode, quiet_zone):
    """
    Prints the QR Code to the terminal.

    :param qrcode: The QR Code.
    :param quiet_zone: The quiet zone (may be zero)
    """
    if sys.platform == 'win32':
        _write_terminal_win(qrcode, quiet_zone=quiet_zone)
    else:
        print(qrcode.terminal(quiet_zone=quiet_zone))


#
# Taken and adapted from segno.writers
#
def _write_terminal_win(qr, quiet_zone=None):  # pragma: no cover
    """\
    Function to write a QR Code to a MS Windows terminal.
    """
    def matrix_iter(matrix):
        """\
        Returns an interator / generator over the provided matrix which includes
        the border and the scaling factor.

        If either the `scale` or `border` value is invalid, a py:exc:`ValueError`
        is raised.

        :param matrix: An iterable of bytearrays.
        :param int version: A version constant.
        :param int scale: The scaling factor (default: ``1``).
        :param int border: The border size or ``None`` to specify the
                default quiet zone (4 for QR Codes, 2 for Micro QR Codes).
        :raises: py:exc:`ValueError` if an illegal scale or border value is provided
        """
        width, height = qr.symbol_size(scale=1, quiet_zone=0)

        def get_bit(i, j):
            return 0x1 if (0 <= i < height and 0 <= j < width and matrix[i][j]) else 0x0

        for i in range(-quiet_zone, height + quiet_zone):
            yield chain.from_iterable(([get_bit(i, j)] for j in range(-quiet_zone, width + quiet_zone)))

    import sys
    import struct
    import ctypes
    from itertools import chain
    from functools import partial
    write = sys.stdout.write
    std_out = ctypes.windll.kernel32.GetStdHandle(-11)
    csbi = ctypes.create_string_buffer(22)
    res = ctypes.windll.kernel32.GetConsoleScreenBufferInfo(std_out, csbi)
    if not res:
        raise OSError('Cannot find information about the console. '
                      'Not running on the command line?')
    default_color = struct.unpack(b'hhhhHhhhhhh', csbi.raw)[4]
    set_color = partial(ctypes.windll.kernel32.SetConsoleTextAttribute, std_out)
    colours = (240, default_color)
    for row in matrix_iter(qr.code):
        prev_bit = -1
        cnt = 0
        for bit in row:
            if bit == prev_bit:
                cnt += 1
            else:
                if cnt:
                    set_color(colours[prev_bit])
                    write('  ' * cnt)
                prev_bit = bit
                cnt = 1
        if cnt:
            set_color(colours[prev_bit])
            write('  ' * cnt)
        set_color(default_color)  # reset color
        write('\n')


if __name__ == '__main__':  # pragma: no cover
    main()
