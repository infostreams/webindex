#!/bin/sh

exec 2>&1
export ODBCINI=/etc/odbc.ini
cd `dirname $0`/engine
python main.py $*
cd ..
