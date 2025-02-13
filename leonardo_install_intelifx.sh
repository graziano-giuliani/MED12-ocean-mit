#!/bin/bash
MIT=/leonardo/home/userexternal/ggiulian/MITgcm

PRJ=$MIT/verification/MED_standalone

source $HOME/modules

rm -rf $PRJ/build
mkdir $PRJ/build
cd $PRJ/build

$MIT/tools/genmake2 -rootdir=$MIT \
   -of=$PRJ/opt/ictp_leonardo_intel.cfg -mods=$PRJ/code \
   -make=gmake -mpi
make depend
make
