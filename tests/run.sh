#!/bin/bash -e

#This script's directory
DIR=$(cd $(dirname "$0"); pwd)

#Enter the tests directory
cd $DIR

#Run each test, for python 2
echo '**********************************'
echo '*'
echo '* Running Python 2'
echo '*'
echo '**********************************'
source ../py2/bin/activate
nosetests -s

#Run each test, for python 3
echo '**********************************'
echo '*'
echo '* Running Python 3'
echo '*'
echo '**********************************'
source ../py3/bin/activate
nosetests -s