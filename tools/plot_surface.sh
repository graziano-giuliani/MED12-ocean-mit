#!/bin/bash

rundir=~/project/COUPLED/ocnonly

for file in $rundir/SALT.0*.data
do
  ncfile="`basename $file .data`.nc"
  pngfile="`basename $file .data`.png"
  [ ! -f $ncfile ] && python3 bintonc_salt.py $file
  [ ! -f $pngfile ] && python3 niceplotter.py $ncfile
done
for file in $rundir/THETA.0*.data
do
  ncfile="`basename $file .data`.nc"
  pngfile="`basename $file .data`.png"
  [ ! -f $ncfile ] && python3 bintonc_temp.py $file
  [ ! -f $pngfile ] && python3 niceplotter.py $ncfile
done
