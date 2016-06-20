# Copyright (c) 2013, Michael Nooner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the copyright holder nor the names of its 
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from setuptools import setup
import sys, os.path, shutil

version = '1.2.1'

if sys.version_info < (2, 6, 0) and sys.version_info < (3, 0, 0):
    sys.stderr.write("pyqrcode requires Python 2.6+ or 3.\n")
    sys.exit(1)


#Make the README.rst file the long description
#This only happens when we are building from the
#source.
if os.path.exists('docs/README.rst'):
    print('Reading README.rst file')
    with open( 'docs/README.rst', 'r') as f:
        longdesc = f.read()
    shutil.copyfile('docs/README.rst', 'README.rst')
else:
    longdesc = None

setup(name='PyQRCode',
      packages=['pyqrcode'],
      version=version,
      description='A QR code generator written purely in Python with SVG, EPS, PNG and terminal output.',
      author='Michael Nooner',
      author_email='mnooner256@gmail.com',
      url='https://github.com/mnooner256/pyqrcode',
      keywords=['qrcode', 'qr'],
      license='BSD',
      extras_require = {
        'PNG':  ["pypng>=0.0.13"],
      },
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        ],
      long_description=longdesc,
)

if os.path.exists('docs/README.rst'):
    os.remove('README.rst')
