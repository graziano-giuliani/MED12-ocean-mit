#!/bin/bash

basedir=$PWD

if [ ! -d CHyM_cpl ]
then
    git clone https://github.com/graziano-giuliani/CHyM_cpl.git CHyM_cpl
fi

if [ ! -d RegCM ]
then
    git clone https://github.com/ICTP/RegCM.git RegCM
fi

if [ ! -d ../MITgcm ]
then
    git clone https://github.com/graziano-giuliani/MITgcm.git ../MITgcm
fi

if [ ! -d RegESM ]
then
    git clone https://github.com/graziano-giuliani/RegESM.git
fi

set -x
{
cd CHyM_cpl && make && cd $basedir
cd RegCM && git checkout CORDEX-5 && autoreconf -f -i && \
    ./configure --enable-clm45 --enable-cpl && \
    make version && make install && cd $basedir
cd MITgcm && bash leonardo_install_intelifx.sh && cd $basedir
cd RegESM && autoreconf -f -i && ./configure --with-atm=$basedir/RegCM \
    --with-ocn=$basedir/MITgcm/build --with-rtm=$basedir/CHyM_cpl && \
    make install && cd $basedir
}

echo "Compiled!'

