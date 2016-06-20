#!/bin/bash -e

#Check that print statements did not get left in by accident.
if grep -n --color '^[[:space:]]\+print' pyqrcode/*.py tests/*.py; then
  echo 'Cleanup debug code!!'
  exit
else
  echo 'No print statements found'
fi

#Remove tox cache, pycache, and pyc files
if [ -d .tox ] ; then
  rm -rf .tox
fi
find . -name '__pycache__' -type d | xargs rm -rf
find . -name '*.pyc' | xargs rm -f

#Build documentation
pushd docs
make html
popd

#This script updates the library's PIPY page and
#uploads the code in tar.gz and .zip formats.
python setup.py register
python setup.py sdist --formats=gztar,zip upload
python setup.py upload_docs --upload-dir docs/_build/html

echo "Done"
