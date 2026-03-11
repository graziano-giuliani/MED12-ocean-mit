#!/usr/bin/env python3

# Produce the OBCS boundary condition from remapped and filled dataset
# Usage:
#         python3 produce_bc.py [directory of processed remapped data]

import os
import sys
import glob
import yaml
from netCDF4 import Dataset
import numpy as np

cpath = "config.yaml"
with open(cpath,"r") as f:
    config = yaml.safe_load(f)
source = config["source_obcs"]
start_year = config["start_year"]
start_month = config["start_month"]
end_year = config["end_year"]
end_month = config["end_month"]
bndys = ['North','South','East','West']

startdate = start_year * 100 + start_month
if end_year > 0:
    enddate = end_year * 100 + end_month
else:
    enddate = -1

try:
    variables = config[source]['variables_obcs'].split(' ')
except:
    sys.exit(0)
try:
    os.mkdir('obcs')
except:
    pass

def boundary(da,config,fout):
    if len(np.shape(da)) == 4:
      if config['boundary']['North']['active']:
          j = config['boundary']['North']['j']
          values = da[0,:,j,:].data
          values.astype('>f4').tofile(fout['North'])
      if config['boundary']['South']['active']:
          j = config['boundary']['South']['j']
          values = da[0,:,j,:].data
          values.astype('>f4').tofile(fout['South'])
      if config['boundary']['East']['active']:
          i = config['boundary']['East']['i']
          values = da[0,:,:,i].data
          values.astype('>f4').tofile(fout['East'])
      if config['boundary']['West']['active']:
          i = config['boundary']['West']['i']
          values = da[0,:,:,i].data
          values.astype('>f4').tofile(fout['West'])
    else:
      if config['boundary']['North']['active']:
          j = config['boundary']['North']['j']
          values = da[0,j,:].data
          values.astype('>f4').tofile(fout['North'])
      if config['boundary']['South']['active']:
          j = config['boundary']['South']['j']
          values = da[0,j,:].data
          values.astype('>f4').tofile(fout['South'])
      if config['boundary']['East']['active']:
          i = config['boundary']['East']['i']
          values = da[0,:,i].data
          values.astype('>f4').tofile(fout['East'])
      if config['boundary']['West']['active']:
          i = config['boundary']['West']['i']
          values = da[0,:,i].data
          values.astype('>f4').tofile(fout['West'])

if source == 'oras5':
    try:
        oras5dir = sys.argv[1]
    except:
        oras5dir = "../ORAS5_MIT"
    for var in variables:
        gpath = os.path.join(oras5dir,var,"*monthly*.nc")
        files = sorted(glob.glob(os.path.expanduser(gpath)))
        xfiles = list(os.path.splitext(os.path.basename(x))[0] for x in files)
        dates = list(int(y[5]) for y in (x.split('_') for x in xfiles))
        if enddate < 0:
            enddate = dates[-1]
        fout = { }
        for bndy in bndys:
            outname = os.path.join('obcs',bndy + '_' + var + '_' +
                       repr(startdate) + '_' +repr(enddate)+'.bin')
            try:
                os.unlink(outname)
            except:
                pass
            fout[bndy] = open(outname, "wb")
        for o,f,d in zip(xfiles,files,dates):
            if d >= startdate and d <= enddate:
                print(var+": "+repr(d))
                boundary(Dataset(f).variables[var],config,fout)
else:
    try:
        inpdir = sys.argv[1]
    except:
        print('Need input directory name')
        sys.exit(1)
    for var in variables:
        gpath = os.path.join(inpdir,var,"*year????_mon??.nc")
        files = sorted(glob.glob(os.path.expanduser(gpath)))
        xfiles = list(os.path.splitext(os.path.basename(x))[0] for x in files)
        dates = list(int(y[7][4:]+y[8][3:])
                     for y in (x.split('_') for x in xfiles))
        if enddate < 0:
            enddate = dates[-1]
        fout = { }
        for bndy in bndys:
            outname = os.path.join('obcs',bndy + '_' + var + '_' +
                       repr(startdate) + '_' +repr(enddate)+'.bin')
            try:
                os.unlink(outname)
            except:
                pass
            fout[bndy] = open(outname, "wb")
        for o,f,d in zip(xfiles,files,dates):
            if d >= startdate and d <= enddate:
                print(var+": "+repr(d))
                boundary(Dataset(f).variables[var],config,fout)

print('Done')
