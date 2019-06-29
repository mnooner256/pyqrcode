# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 - 2018 -- Lars Heuer - Semagia <http://www.semagia.com/>.
# All rights reserved.
#
# License: BSD License
#
"""\
Tests against the command line script.
"""
from __future__ import absolute_import, unicode_literals
import os
import tempfile
import pytest
from pyqrcodeng import cli


def test_defaults():
    args = cli.parse([''])
    assert args.content == ['']
    assert 'H' == args.error
    assert args.mode is None
    assert args.version is None
    assert args.scale == 1
    assert args.output is None
    assert 4 == args.quiet_zone
    assert args.module_color is None
    assert args.background is None
    # SVG
    assert args.xmldecl
    assert not args.no_classes
    assert args.title is None
    assert args.svgns is True
    assert args.svgclass is None
    assert args.lineclass is None
    assert args.omithw is False


def test_segno_version():
    with pytest.raises(SystemExit) as e:
        cli.parse(['--ver', ''])
        assert 0 == e.exception.code


def test_segno_version_shortcut():
    with pytest.raises(SystemExit) as e:
        cli.parse(['-V', ''])
        assert 0 == e.exception.code


def test_noargs():
    with pytest.raises(SystemExit) as e:
        cli.parse([])
        assert 1 == e.exception.code


def test_error():
    args = cli.parse(['-e', 'm', ''])
    assert args.error == 'M'
    qr = cli.make_code(args)
    assert 'M' == qr.error


def test_error2():
    args = cli.parse(['-e', 'M', ''])
    assert args.error == 'M'
    qr = cli.make_code(args)
    assert 'M' == qr.error


def test_error3():
    args = cli.parse(['123'])
    assert 'H' == args.error
    qr = cli.make_code(args)
    assert 1 == qr.version
    assert 'H' == qr.error


def test_error4():
    args = cli.parse(['--error=q', ''])
    assert args.error == 'Q'
    qr = cli.make_code(args)
    assert 'Q' == qr.error


def test_version():
    args = cli.parse(['-v', '1', ''])
    assert '1' == args.version
    qr = cli.make_code(args)
    assert 1 == qr.version


def test_version2():
    args = cli.parse(['--version', '40', ''])
    assert args.version == '40'
    qr = cli.make_code(args)
    assert 40 == qr.version


def test_mode():
    args = cli.parse(['-m', 'alphanumeric', 'A'])
    assert args.mode == 'alphanumeric'
    qr = cli.make_code(args)
    assert 'alphanumeric' == qr.mode


def test_mode2():
    args = cli.parse(['--mode=byte', ''])
    assert args.mode == 'byte'
    qr = cli.make_code(args)
    assert 'binary' == qr.mode


def test_border():
    args = cli.parse(['--quietzone', '0', ''])
    assert args.quiet_zone == 0


def test_border_shortcut():
    args = cli.parse(['-qz', '10', ''])
    assert args.quiet_zone == 10


def test_scale():
    args = cli.parse(['--scale=1.6', ''])
    assert args.scale == 1.6


def test_scale2():
    args = cli.parse(['--scale=2.0', ''])
    assert args.scale == 2
    assert isinstance(args.scale, int)


def test_scale_shortcut():
    args = cli.parse(['-s=1.6', ''])
    assert args.scale == 1.6


def test_color():
    args = cli.parse(['--color', 'green', ''])
    assert args.module_color == 'green'
    assert cli.build_config(args)['module_color'] == 'green'


def test_color_transparent():
    args = cli.parse(['--color=transparent', '-output=x.png', ''])
    assert args.module_color == 'transparent'
    assert cli.build_config(args)['module_color'] is None


def test_color_transparent2():
    args = cli.parse(['--color=trans', '-output=x.png', ''])
    assert args.module_color == 'trans'
    assert cli.build_config(args)['module_color'] is None


def test_background():
    args = cli.parse(['--background', 'red', ''])
    assert args.background == 'red'


def test_background_transparent():
    args = cli.parse(['--background=transparent', '-output=x.png', ''])
    assert args.background == 'transparent'
    assert cli.build_config(args)['background'] is None


def test_background_transparent2():
    args = cli.parse(['--background=trans', '-output=x.png', ''])
    assert args.background == 'trans'
    assert cli.build_config(args)['background'] is None


def test_error_code():
    with pytest.raises(SystemExit) as e:
        cli.main(['--version=41', '"This is a test"'])
        assert 1 == e.exception.code
        assert e.exception.message


def test_unsupported_fileformat():
    with pytest.raises(SystemExit) as e:
        cli.main(['--output=test.pdf', '"This is a test"'])
        assert 1 == e.exception.code
        assert e.exception.message


def test_unsupported_color():
    with pytest.raises(SystemExit) as e:
        cli.main(['--color=test', '--output=test.png', '"This is a test"'])
        assert 1 == e.exception.code
        assert e.exception.message


@pytest.mark.parametrize('arg', ['-o', '--output'])
@pytest.mark.parametrize('ext, expected, mode', [('svg', b'<?xml ', 'rb'),
                                                 ('png', b'\211PNG\r\n\032\n', 'rb'),
                                                 ('eps', '%!PS-Adobe-3.0 EPSF-3.0', 'rt'),])
def test_output(arg, ext, expected, mode):
    f = tempfile.NamedTemporaryFile('w', suffix='.{0}'.format(ext), delete=False)
    f.close()
    try:
        cli.main(['test', arg, f.name])
        f = open(f.name, mode=mode)
        val = f.read(len(expected))
        f.close()
        assert expected == val
    finally:
        os.unlink(f.name)


def test_terminal(capsys):
    cli.main(['test'])
    out, err = capsys.readouterr()
    assert out
    assert '' == err


# -- SVG
def test_xmldecl():
    args = cli.parse(['--output=x.svg', ''])
    assert args.xmldecl
    assert cli.build_config(args)['xmldecl'] is True


def test_omit_xmldecl():
    args = cli.parse(['--no-xmldecl', '--output=x.svg', ''])
    assert not args.xmldecl
    assert cli.build_config(args)['xmldecl'] is False


def test_not_omit_classes():
    args = cli.parse(['--output=x.svg', ''])
    assert not args.no_classes
    config = cli.build_config(args)
    assert 'svgclass' not in config
    assert 'lineclass' not in config


def test_omit_classes():
    args = cli.parse(['--no-classes', '--output=x.svg', ''])
    assert args.no_classes
    config = cli.build_config(args)
    assert config['svgclass'] is None
    assert config['lineclass'] is None


def test_title():
    args = cli.parse(['--output=x.svg', ''])
    assert args.title is None
    assert cli.build_config(args)['title'] is None


def test_title2():
    args = cli.parse(['--title=Magnolia', '--output=x.svg', ''])
    assert args.title == 'Magnolia'
    assert cli.build_config(args)['title'] == 'Magnolia'


def test_ns():
    args = cli.parse(['--output=x.svg', ''])
    assert args.svgns is True
    assert cli.build_config(args)['svgns'] is True


def test_ns2():
    args = cli.parse(['--no-namespace', '--output=x.svg', ''])
    assert not args.svgns
    assert cli.build_config(args)['svgns'] is False


def test_svgclass():
    args = cli.parse(['--output=x.svg', ''])
    assert args.svgclass is None
    assert 'svgclass' not in cli.build_config(args)


def test_svgclass2():
    args = cli.parse(['--svgclass=magnolia', '--output=x.svg', ''])
    assert args.svgclass == 'magnolia'
    assert cli.build_config(args)['svgclass'] == 'magnolia'


def test_svg_lineclass():
    args = cli.parse(['--output=x.svg', ''])
    assert args.lineclass is None
    assert 'lineclass' not in cli.build_config(args)


def test_svg_lineclass2():
    args = cli.parse(['--lineclass=magnolia', ''])
    assert args.lineclass == 'magnolia'
    assert cli.build_config(args)['lineclass'] == 'magnolia'


def test_omitsize():
    args = cli.parse(['--output=x.svg', ''])
    assert not args.omithw
    assert cli.build_config(args)['omithw'] is False


def test_omitsize2():
    args = cli.parse(['--no-size', ''])
    assert args.omithw
    assert cli.build_config(args)['omithw'] is True


if __name__ == '__main__':
    pytest.main([__file__])
