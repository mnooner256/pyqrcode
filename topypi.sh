#!/bin/bash -e

#Clean up any .py and pycache files
for 

#This script updates the libraries PIPY page and
#uploads the code in tar.gz and .zip formats.
python setup.py register
python setup.py sdist --formats=gztar,zip upload

pushd docs
make html

pushd _build/html/
zip -r ../../../docs.zip *
popd
popd

echo
echo "Be sure to change the version on PyPi's website!!!"
echo "Also, reupload the documentation zip file!"
echo

#Clean up the egg info directory
rm -rf *egg-info