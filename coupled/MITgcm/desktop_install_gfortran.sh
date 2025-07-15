#!/bin/bash

MIT=/home/netapp-clima/users/ggiulian/MED12-ocean-mit/MITgcm

PRJ=$PWD

cd $PRJ/code && ln -sf SIZE_desktop.h SIZE.h && cd $PRJ
mkdir -p $PRJ/build && cd $PRJ/build

cp /usr/lib/x86_64-linux-gnu/openmpi/include/mpif.h .
$MIT/tools/genmake2 -rootdir=$MIT \
   -of=$PRJ/opt/desktop_gfortran.cfg -mods=$PRJ/code \
   -make=make -mpi
make depend
make
