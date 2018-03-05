#!/bin/bash

lambda-package-base.sh
rm lambda/lib/python2.7/site-packages/osgeo
ln -s GDAL-2.2.2-py2.7-linux-x86_64.egg/osgeo lambda/lib/python2.7/site-packages/osgeo