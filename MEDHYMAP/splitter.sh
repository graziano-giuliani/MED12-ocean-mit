#!/bin/bash

for file in orig/*_ok.nc
do
  echo $file
  tmpbase=`basename $file .nc`_mon
  cdo splitmon $file $tmpbase
  for sfile in ${tmpbase}*
  do
    echo $sfile
    cdo selvar,temperature $sfile temperature/$sfile
    cdo selvar,salinity $sfile salinity/$sfile
  done
  rm ${tmpbase}*
done
