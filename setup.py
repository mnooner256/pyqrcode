from setuptools import setup
import sys, os.path

version = '0.9'

if sys.version_info < (3, 0, 0):
    sys.stderr.write("pyqrcode requires Python 3.\n")
    sys.exit(1)


#Make the README.rst file the long description
#This only happens when we are building from the
#source.
if os.path.exists('doc/README.rst'):
    print('Reading README.rst file')
    with open( 'doc/README.rst', 'r') as f:
        longdesc = f.read()
else:
    longdesc = None

setup(name='PyQRCode',
      packages=['pyqrcode'],
      version=version,
      description='A QR code generator written purely in python 3 with SVG and PNG output.',
      author='Michael Nooner',
      author_email='mnooner256@gmail.com',
      url='https://github.com/mnooner256/pyqrcode',
      keywords=['qrcode', 'qr'],
      extras_require = {
        'PNG':  ["pypng>=0.0.13"],
      },
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        ],
      long_description=longdesc,
)
