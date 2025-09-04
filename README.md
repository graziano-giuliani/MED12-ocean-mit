![University of  Trieste](UNITS.jpg)

This repository contains the glue linking together the pieces composig the
RegCM-ES1-1, the Regional Earth System Moddel of UNESCO ICTP which is used
for the MED-CORDEX simulation run by the ICTP in collaboration with OGS and
the University of Trieste.

Following here you can find the procedure followed to prepare the run.

The RegCM5 component is not here described.

# Create the MITgcm grid

  * We use for the MED the global NEMO ORCA grid, from which we cut down
    the area of interest. You can download the global grid from here:

      `http://clima-dods.ictp.it/MITGCM/coordinates_ORCA_R12.nc`

    Copy the data file in the **grid** directory.

  * Compile the program **create_coordinates** (source extracted from NEMO
    code, see LICENSE) by entering the src directory and typing **make**.
    Copy the executable in the above grid directory.

  * The configuration in the namelist **namelist_R12** is for the MED12
    experiment. Edit it to localize somewhere else. Run this afterward:

      > ./create_coordinates namelist_R12

    This will create the output file **1_coordinates_ORCA_R12.nc**

  * The vertical information is saved into the **depth.nc** file. Modify it
    to your necessity.

  * The boundary area can be configurated on any of the sides by changing the
    file **rbcsbdy.yaml**. Note that for complex boundaries, it is best to
    manually edit the rbcs mask file. The settings in there are consistent
    with the MED experiment.

  * Extract the information required by the MITgcm by running the python
    program:

      > python3 coordinates2mit.py

# Stand alone MITgcm model build

  * Download model code (I use my fork here):

     > git clone https://github.com/graziano-giuliani/MITgcm.git

  * Modify the file **leonardo_install_intelifx.sh**. This script must point to
    the MITgcm root directory (MIT). The PRJ should be the current directory.
    The user must have an opt file in the opt directory with compiler,
    library and system generalities (I have a GNU, Intel ifort and Intel ifx
    templates there).

  * The code contains the modding. Important is the **SIZE.h** which must match
    the system computational platform.

  * Run the script, in the build the code would compile in mitgcmuv

# Bathymetry, initial condition and external forcings creation
    
  * We created EMODnet Mediterranean grid by merging togheter original tiles of
    EMODnet Bathymetry DTM Tiles [https://emodnet.ec.europa.eu/geoviewer/].
    Result in Mediterranean_basin.nc here:

      `http://clima-dods.ictp.it/MITGCM/Mediterranean_basin.nc`

    An ETOPO high resolution dataset for global can instead be had here:

      `http://clima-dods.ictp.it/regcm4/SURFACE/ETOPO_BTM_30s.nc`

  * Download any of the above into the bathy directory.

  * For the med, we use a cdo command using a distance weighted remapping
    using 128 points around the target one.

     > python3 remap_bathymetry.py

  * Fine tuning, binary and mask creation:

     > python3 zero_out.py

    Copy the **mask.nc** file into **ORAS5_MIT** and **ERA5** directories.

  * Download ORAS5 dataset in directory ORAS5:

     > python3 download.py

     > mkdir sossheig vosaline votemper

     > mv votemper*nc votemper

     > mv vosaline*nc vosaline

     > mv sossheig*nc sossheig

  * Interpolate ORAS5 dataset to MIT in directory ORAS5_MIT:

     > python3 process_oras_3d.py ../ORAS5/vosaline

     > python3 process_oras_3d.py ../ORAS5/votemper

     > python3 process_oras_2d.py ../ORAS5/sossheig

  * Download ERA5 dataset in directory ERA5:

     > python3 download_surface_monthly.py

  * Compute the specific humidity from the Dewpoint temperature. An example
    script doing the job is provided.

  * Process ERA5 data to be used as external forcings in ERA5:

     > python3 process_era5_2d.py

  * We are now ready to prepare the initial and boundary conditions.
    In the **input** direcory, a yaml config file contains the start
    year and month of the simulation and the number of decades to
    average into the initial condition file. Edit it to suit your
    necessities.

  * Create binary boundary conditions:

     > python3 produce_bc.py

  * Compute monthly decadal averages to be used as initial conditions:

     > python3 produce_ic.py

  * Create external forcings data: 

     > python3 produce_extf.py

  * All the binary input files should now be ready!

# Run the model

  Now that we have the input data, link all the **bin** files in the input
  directory in the **run** directory. Link there all the files in the **data**
  ditrectory. Link the model binary **mitgcmuv**. Create your job to submit.
  This is our first experiment log.

# Protocol

  https://zenodo.org/records/11659642
