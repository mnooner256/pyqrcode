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
    raise ValueError('{0} is not a directory.'.format(code_dir))


if len(sys.argv) > 1:
    v=int(sys.argv[1])
if len(sys.argv) > 2:
    s=int(sys.argv[2])

#for i in range(1, v+1):
#    print('Generating version {0}'.format(i))
#    try:
code = pyqrcode.QRCode(data, error=error, version=version, mode=mode)
print(code.terminal())
code.png('{0}/v{1}.png'.format(code_dir, code.version), scale)
#code.svg('{0}/v{1}.svg'.format(code_dir, code.version), scale, background="white")

print('Error={0}\nVersion={1}\nMode={2}\nScale={3}'.format(code.error, code.version, code.mode, scale))
#    except ValueError:
#        print('Version {0} will not fit'.format(i))
#        pass
