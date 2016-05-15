#!/bin/bash -e

#Remove tox cache, pycache, and pyc files
if [ -d .tox ] ; then
  rm -rf .tox
fi
find . -name '__pycache__' -type d | xargs rm -rf
find . -name '*.pyc' | xargs rm -f

#Build documentation
pushd docs
make html

#Create the documentation zip file
pushd _build/html/
zip -r ../../../docs.zip *
popd
popd

#This script updates the library's PIPY page and
#uploads the code in tar.gz and .zip formats.
python setup.py register
python setup.py sdist --formats=gztar,zip upload

echo
echo "Be sure to change the version on PyPi's website!!!"
echo "Also, reupload the documentation zip file!"
echo
