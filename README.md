# Protocol

  https://zenodo.org/records/11659642

# Bathymetry creation

  * Extracted grid information MIT_MED.grid from LATC,LONC files
  * Create all the binary data from the netCDF data in the input directory:
     for file in *nc; do python3 nc_to_bin.py $file; done;
  * Created EMODnet Mediterranean grid by merging togheter original tiles
     EMODnet Bathymetry DTM Tiles
      https://emodnet.ec.europa.eu/geoviewer/
    Result in Mediterranean_basin.nc
  * Interpolated the above file using:
     cdo remapdis,MIT_MED.grid,128 Mediterranean_basin.nc MIT_MED.nc
  * Zero out unwanted Atlantic patches:
     python3 zero_out.py MIT_EMODnet_MED.nc MED_BLACK_BATHY.nc
  * Create the mask file:
     ncks -v mask MED_BLACK_BATHY.nc mask.nc
  * Download ORAS5 dataset in directory ORAS5:
     python3 download.py
     mkdir sossheig vosaline votemper
     mv votemper*nc votemper
     mv vosaline*nc vosaline
     mv sossheig*nc sossheig
  * Interpolate ORAS5 dataset to MED in directory ORAS5_MED:
     python3 process_oras_3d.py ~/project/MITGCM/ORAS5/vosaline
     python3 process_oras_3d.py ~/project/MITGCM/ORAS5/votemper
     python3 process_oras_2d.py ~/project/MITGCM/ORAS5/sossheig
     mv votemper*nc votemper
     mv vosaline*nc vosaline
     mv sossheig*nc sossheig
  * Create binary boundary conditions in input directory:
     python3 produce_ic.py ~/project/MITGCM/ORAS5_MED/votemper
     python3 produce_ic.py ~/project/MITGCM/ORAS5_MED/vosaline
     python3 produce_ic.py ~/project/MITGCM/ORAS5_MED/sossheig
  * Compute August averages for the two decades 1970-1980 for IC:
     ncrcat ORAS5_MED/vosaline/vosaline_control_monthly_highres_3D_19[7-8]08* \
               vosaline_august_1970-1980.nc
     ncra vosaline_august_1970-1980.nc \
           input/vosaline_control_monthly_highres_3D_197x08-198x08_mean.nc
     python3 nc_to_bin.py \
           input/vosaline_control_monthly_highres_3D_197x08-198x08_mean.nc
     ncrcat ORAS5_MED/vosaline/votemper_control_monthly_highres_3D_19[7-8]08* \
               votemper_august_1970-1980.nc
     ncra votemper_august_1970-1980.nc \
           input/votemper_control_monthly_highres_3D_197x08-198x08_mean.nc
     python3 nc_to_bin.py \
           input/votemper_control_monthly_highres_3D_197x08-198x08_mean.nc
  * Process ERA5 data to be used as external forcings in ERA5:
     python3 process_era5_2d.py
  * Create binary external forcings in input directory:
     python3 process_era5_2d.py ~/project/MITGCM/ERA5/apressure
     python3 process_era5_2d.py ~/project/MITGCM/ERA5/aqh
     python3 process_era5_2d.py ~/project/MITGCM/ERA5/atemp
     python3 process_era5_2d.py ~/project/MITGCM/ERA5/evap
     python3 process_era5_2d.py ~/project/MITGCM/ERA5/lwflux
     python3 process_era5_2d.py ~/project/MITGCM/ERA5/precip
     python3 process_era5_2d.py ~/project/MITGCM/ERA5/runoff
     python3 process_era5_2d.py ~/project/MITGCM/ERA5/swflux
     python3 process_era5_2d.py ~/project/MITGCM/ERA5/uwind
     python3 process_era5_2d.py ~/project/MITGCM/ERA5/vwind
  * Store all the bin files from the input directory together as the input data.
