"""Download ERA5.py

This script can be used to download ERA5 data on model levels using the CDS API.
Please see the installation instructions: https://cds.climate.copernicus.eu/api-how-to
You need to have a valid CDS API key and you need to pip install cdsapi.

For model levels the following variables are downloaded:
  - u, v, q on selected levels
  - tp, e, sp, and tcw at the surface

Modify the settings below, then run with:

python download_era5_ml.py
"""
from pathlib import Path

import cdsapi
import pandas as pd

target_dir = "."
skip_exist = True

datelist = pd.date_range("20260125", "20260215")

months = ["01", "02"]
# días solo para cada mes (se usan por separado dentro del bucle)
days_all = {
    "01": ["25", "26", "27", "28", "29", "30", "31"],
    "02": [f"{d:02d}" for d in range(1, 16)],
}

dates = [
    "2026-01-25/to/2026-01-31",
    "2026-02-01/to/2026-02-15",
]

area = [25, -80, -20, -15] # None for global, or [N, W, S, E]
grid = [0.25, 0.25]

times = [
    "00:00",
    "01:00",
    "02:00",
    "03:00",
    "04:00",
    "05:00",
    "06:00",
    "07:00",
    "08:00",
    "09:00",
    "10:00",
    "11:00",
    "12:00",
    "13:00",
    "14:00",
    "15:00",
    "16:00",
    "17:00",
    "18:00",
    "19:00",
    "20:00",
    "21:00",
    "22:00",
    "23:00",
]

levels = (
    "20/40/60/80/90/95/100/105/110/115/120/123/125/128/130/131/132/133/134/135/136/137"
)

ml_variables = {
    "u": 131,
    "v": 132,
    "q": 133,
}

surface_variables = {
    "tp": "total_precipitation",
    "e": "evaporation",
    "sp": "surface_pressure",
    "tcw": "total_column_water",
}

## The part below should not have to be modified
################################################

c = cdsapi.Client(timeout=600,quiet=False)

ind = 0
# We want one file per variable per day
# Modified to one file per variable per month   ###
#for date in datelist:
for month in months:
    outfolder = Path(target_dir) / "2026" / f"{month}"
    outfolder.mkdir(exist_ok=True, parents=True)

    this_days = days_all[month]

    # Download surface variables (solo los días seleccionados del mes)
    for variable, long_name in surface_variables.items():
        outfile = f"ERA5_2026-{month}_{variable}.nc"
        if (outfolder / outfile).exists() and skip_exist:
            print(f"{outfolder / outfile} already exists, skipping. Set skip_exist = False to force re-download")
        else:
            try:
                c.retrieve(
                    "reanalysis-era5-single-levels",
                    {
                        "product_type": "reanalysis",
                        "variable": long_name,
                        "year": "2026",
                        "month": month,
                        "day": this_days,
                        "time": times,
                        "area": area,
                        "grid": grid,
                        "format": "netcdf",
                    },
                    str(outfolder / outfile),
                )
            except Exception as e:
                print(e)
                print(f"Request failed for {variable}, {month}. Proceeding.")

    # Download 3d variables (usa dates por mes / rango)
    for variable, param in ml_variables.items():
        outfile = f"ERA5_2026-{month}_ml_{variable}.nc"
        if (outfolder / outfile).exists() and skip_exist:
            print(f"{outfolder / outfile} already exists, skipping. Set skip_exist = False to force re-download")
        else:
            try:
                c.retrieve(
                    "reanalysis-era5-complete",
                    {
                        "time": times,
                        "dates": dates[ind],
                        "levelist": levels,
                        "param": param,
                        "class": "ea",
                        "expver": "1",
                        "levtype": "ml",
                        "stream": "oper",
                        "type": "an",
                        "format": "netcdf",
                        "area": area,
                        "grid": grid,
                    },
                    str(outfolder / outfile),
                )
            except Exception as e:
                print(e)
                print(f"Request failed for {variable}, {month}. Proceeding.")
    ind += 1
