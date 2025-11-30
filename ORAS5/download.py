#!/usr/bin/env python3

import os
import glob
import cdsapi
import zipfile

dataset = "reanalysis-oras5"
client = cdsapi.Client()

for year in range(1958,2015):
    for month in range(1,13):
        request = {
            "product_type": ["consolidated"],
            "vertical_resolution": "all_levels",
            "variable": [
                "potential_temperature",
                "salinity"
            ],
            "year": [repr(year)],
            "month": [f"{month:02d}"]
        }
        client.retrieve(dataset, request).download()
        zipf = glob.glob('*.zip')[0]
        with zipfile.ZipFile(zipf,"r") as zz:
            zz.extractall("./")
        os.unlink(zipf)
        request = {
            "product_type": ["consolidated"],
            "vertical_resolution": "single_level",
            "variable": ["sea_surface_height"],
            "year": [repr(year)],
            "month": [f"{month:02d}"]
        }
        client = cdsapi.Client()
        client.retrieve(dataset, request).download()
        zipf = glob.glob('*.zip')[0]
        with zipfile.ZipFile(zipf,"r") as zz:
            zz.extractall("./")
        os.unlink(zipf)

for year in range(2015,2025):
    for month in range(1,13):
        request = {
            "product_type": ["operational"],
            "vertical_resolution": "all_levels",
            "variable": [
                "potential_temperature",
                "salinity"
            ],
            "year": [repr(year)],
            "month": [f"{month:02d}"]
        }
        client.retrieve(dataset, request).download()
        zipf = glob.glob('*.zip')[0]
        with zipfile.ZipFile(zipf,"r") as zz:
            zz.extractall("./")
        os.unlink(zipf)
        request = {
            "product_type": ["operational"],
            "vertical_resolution": "single_level",
            "variable": ["sea_surface_height"],
            "year": [repr(year)],
            "month": [f"{month:02d}"]
        }
        client = cdsapi.Client()
        client.retrieve(dataset, request).download()
        zipf = glob.glob('*.zip')[0]
        with zipfile.ZipFile(zipf,"r") as zz:
            zz.extractall("./")
        os.unlink(zipf)
