# -*- coding: utf-8 -*-
# Released into the public domain by Teran McKinney.
"""
qrprint: CLI application for PyQRCode to print a QR code into a terminal.
"""

import argparse

import pyqrcode


def main():
    """
    Where we should be called. Just a CLI application, no use using this as
    a library.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('text', help='text for QR code')
    parser.add_argument('--module_color',
                        help='Sets QR code data module color',
                        default='default')
    parser.add_argument('--background',
                        help='Sets QR code background',
                        default='reverse')
    parser.add_argument('--quiet_zone',
                        help='Sets QR code quiet zone',
                        default=4)
    args = parser.parse_args()
    qr = pyqrcode.create(args.text)
    print(qr.terminal(module_color=args.module_color,
                      background=args.background,
                      quiet_zone=args.quiet_zone))
    return True

if __name__ == '__main__':
    main()
