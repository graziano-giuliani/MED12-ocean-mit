#!/bin/bash

MIT=/leonardo/home/userexternal/aanubha0/MED12-ocean-mit/MITgcm
PRJ=$PWD

cd $PRJ/build

$MIT/tools/genmake2 -rootdir=$MIT \
   -of=$PRJ/opt/ictp_leonardo_intel.cfg -mods=$PRJ/code \
   -make=gmake -mpi
make depend
make
