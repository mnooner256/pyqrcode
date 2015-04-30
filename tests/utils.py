# -*- coding: utf-8 -*-
"""\
Test utilities.
"""
import os
import png


def _make_pixel_array(pixels, greyscale):
    """\
    Returns a list of lists. Each list contains 0 and/or 1.
    0 == black, 1 == white.

    `greyscale`
        Indiciates if this function must convert RGB colors into black/white.
    """
    def bw_color(r, g, b):
        rgb = r, g, b
        if rgb == (0, 0, 0):
            return 0
        elif rgb == (255, 255, 255):
            return 1
        else:
            raise ValueError('Unexpected RGB tuple: {0})'.format(rgb))
    res = []
    if greyscale:
        for row in pixels:
            res.append(list(row[:]))
    else:
        for row in pixels:
            it = [iter(row)] * 3
            res.append([bw_color(r, g, b) for r, g, b in zip(*it)])
    return res


def get_reference_filename(filename):
    """\
    Returns an absolute path to the "reference" filename.
    """
    return os.path.join(os.path.dirname(__file__), 'ref/{}'.format(filename))


def get_png_info(**kw):
    """\
    Returns the width, height and the pixels of the provided PNG file.
    """
    reader = png.Reader(**kw)
    w, h, pixels, meta = reader.asDirect()
    return w, h, _make_pixel_array(pixels, meta['greyscale'])
