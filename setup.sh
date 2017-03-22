#!/bin/sh

exec 2>&1
export ODBCINI=/etc/odbc.ini
cd setup
python setup.py $*
cd ..
