#!/bin/bash

MIT=/leonardo_work/ICT25_ESP/MITGCM/MED12-ocean-mit/MITgcm

PRJ=$PWD

source $HOME/modules
cd $PRJ/code && ln -sf SIZE_leonardo.h SIZE.h && cd $PRJ
mkdir -p $PRJ/build && cd $PRJ/build

$MIT/tools/genmake2 -rootdir=$MIT \
   -of=$PRJ/opt/ictp_leonardo_intel.cfg -mods=$PRJ/code \
   -make=gmake -mpi
make depend
make
