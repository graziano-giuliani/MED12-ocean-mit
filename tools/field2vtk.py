#!/usr/bin/env python3

import sys
import os
import numpy as np
from netCDF4 import Dataset
import vtk
import vtk.util.numpy_support as numpy_support

ifile = sys.argv[1]
vname = sys.argv[2]

np.set_printoptions(threshold=sys.maxsize)

rcmfile = Dataset(ifile,'r')
var = rcmfile.variables[vname][:]

if vname == 'SALT':
    var = np.flip(var,axis=0)

npoints = np.prod(var.shape).item( )
f = open(vname+'.vtk','w')
f.write('# vtk DataFile Version 2.0\n')
f.write(vname+'\n')
f.write('ASCII\n')
f.write('DATASET STRUCTURED_POINTS\n')
f.write('DIMENSIONS '+ ' '.join((repr(x) for x in reversed(var.shape))) + '\n')
f.write('SPACING 0.100000 0.100000 0.100000\n')
f.write('ORIGIN 0 0 0\n')
f.write('POINT_DATA '+ repr(npoints) +'\n')
f.write('SCALARS volume_scalars float 1\n')
f.write('LOOKUP_TABLE default\n')
for val in var.flatten( ):
    f.write(repr(val.item( ))+'\n')
f.close()
