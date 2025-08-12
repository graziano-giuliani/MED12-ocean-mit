#!/bin/bash

#SBATCH --account             CMPNS_ictpclim
#SBATCH --job-name            MED-12_POST
#SBATCH --mail-type           ALL
#SBATCH --mail-user           ggiulian@ictp.it
#SBATCH --nodes               1
#SBATCH --ntasks-per-node     112
#SBATCH --partition           dcgp_usr_prod
###SBATCH --qos                 dcgp_qos_dbg
#SBATCH --time                00:30:00

datadir=$1
idate=$2

pycordex=/leonardo/home/userexternal/ggiulian/RegCM-CORDEX5/Tools/Scripts/pycordexer
mail=ggiulian@ictp.it
domain=MED-12
global=ERA5
experiment=evaluation
ensemble=r1i1p1f1
notes="None"
output="."
proc=20
regcm_model=RegCM-ES
regcm_release=1.1
regcm_version_id=v1-r1

allargs="-m $mail -d $domain -g $global -e $experiment -b $ensemble \
         -n "$notes" -o $output -p $proc --regcm-model-name $regcm_model \
         -r $regcm_release --regcm-version-id $regcm_version_id"

srffile=$datadir/*_SRF.${idate}*.nc
stsfile=$datadir/*_STS.${idate}*.nc
radfile=$datadir/*_RAD.${idate}*.nc
atmfile=$datadir/*_ATM.${idate}*.nc

srfvars=tas,pr,evspsbl,huss,hurs,ps,psl,sfcWind,uas,vas,clt,rsds,rlds
srfvars=$srfvars,ts,prc,prhmax,prsn,tauu,tauv,zmla,prw,rsus,rlus,hfss,hfls
srfvars=$srfvars,ua50m,ua100m,ua150m,va50m,va100m,va150m,ta50m,hus50m
srfvars=$srfvars,mrros,mrro,cape,cin,li,evspsblpot,z0,hfso
stsvars=prmean,psmean,tasmean,tasmax,tasmin,sfcWindmax,sundmean,wsgsmax
radvars=clwvi,clivi,rlut,rsut,rsdt,clh,clm,cll,cld
atmvars=ua,va,ta,hus,zg,wa,mrsol,mrso,tsl,cli,clw

pids=""
$pycordex/pycordexer.py $allargs $srffile $srfvars & pids+="$! "
$pycordex/pycordexer.py $allargs $radfile $radvars & pids+="$! "
$pycordex/pycordexer.py $allargs $stsfile $stsvars & pids+="$! "
$pycordex/pycordexer.py $allargs $atmfile $atmvars & pids+="$! "

for p in $pids; do wait $p || err=$?; done
[[ $err ]] && exit -1

rm $srffile $radfile $stsfile $atmfile
