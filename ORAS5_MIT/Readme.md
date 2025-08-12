# Processing of ORAS5 data

The ORAS5 data in the *ORAS5* directory after download must be
interpolated onto the *MITgcm* grid.
Link the *mask.nc* and *depth.nc* files from the *bathy* directory above.

## Interpolate the data on the MitGCM grid

Run the python-cdo interpolation scripts:

    python3 process_oras_2d.py ~/project/MITGCM/ORAS5/sossheigh
    python3 process_oras_3d.py ~/project/MITGCM/ORAS5/temperature
    python3 process_oras_3d.py ~/project/MITGCM/ORAS5/salinity

