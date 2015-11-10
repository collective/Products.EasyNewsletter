#!/bin/sh

# see https://community.plone.org/t/not-using-bootstrap-py-as-default/620
rm -r ./lib ./include ./local ./bin
ln -fs plone-4.3.x.cfg buildout.cfg
virtualenv --clear .
./bin/pip install --upgrade pip setuptools zc.buildout
./bin/buildout 
