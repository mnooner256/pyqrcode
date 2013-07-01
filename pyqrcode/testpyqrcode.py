#!/usr/bin/env python
#Test against codes generated at:
#   http://www.morovia.com/free-online-barcode-generator/qrcode-maker.php

import pyqrcode
import os, sys

code_dir = './qrtests'
scale = 4

data = 'CSCI 0'
error='H'
version=None
mode='alphanumeric'


if not os.path.exists(code_dir):
    os.mkdir(code_dir)
elif not os.path.isdir(code_dir):
    raise ValueError('{} is not a directory.'.format(code_dir))


if len(sys.argv) > 1:
    v=int(sys.argv[1])
if len(sys.argv) > 2:
    s=int(sys.argv[2])

#for i in range(1, v+1):
#    print('Generating version {}'.format(i))
#    try:
code = pyqrcode.QRCode(data, error=error, version=version, mode=mode)
code.png('{}/v{}.png'.format(code_dir, code.version), scale)
#code.svg('{}/v{}.svg'.format(code_dir, code.version), scale, background="white")

print('Error={}\nVersion={}\nMode={}\nScale={}'.format(code.error, code.version, code.mode, scale))
#    except ValueError:
#        print('Version {} will not fit'.format(i))
#        pass
