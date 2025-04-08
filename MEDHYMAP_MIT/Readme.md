# Processing of MEDHYMAP data

The MEDHYMAP data in the *MEDHYMAP* directory after processing must be
interpolated onto the *MITgcm* grid.

## Create the mask

Copy the *mask.nc* file from the *bathy* directory above and run the python
script *medmask.py* to mask out the Atlantic and Black Sea. 

    python3 medmask.py

## Interpolate the data on the MitGCM grid

Run the python-cdo interpolation script:

    python3 process_medhymap_3d.py temperature ../MEDHYMAP 

    python3 process_medhymap_3d.py salinity ../MEDHYMAP

## Merge the ORAS5 interpoalted data onto Atlantic and Black Sea

Fill in the data not present in MEDHYMAP using ORAS5 reanalysis

    python3 merge_oras5.py ./ ../ORAS5_MIT

The data are now ready to create the input for the *MITgcm*
