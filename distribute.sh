#!/bin/bash -e

#This script updates the libraries PIPY page and
#uploads the code in tar.gz and .zip formats.

python setup.py register
python setup.py sdist --formats=gztar,zip upload

rm -rf build dist *egg*
