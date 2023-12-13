## maridatadownloader

Downloading tools for environmental/marine/weather data.

Currently supported platforms/provider:
 - Global Forecast System (GFS)
 - Copernicus Marine Environment Monitoring Service (CMEMS)
 - Copernicus Climate Data Store (CDS) ECMWF ERA5 reanalysis

Currently supported access services/APIs:
 - OPeNDAP
 - Copernicus CDS API

### Installation

```
pip install git+https://github.com/52North/MariGeoRoute#subdirectory=data/maridatadownloader
```

### Usage

#### Basics

```python
from maridatadownloader import DownloaderFactory

## Create downloader object

# Depending on platform/dataset these might be necessary
kwargs =  {
    'product': <product>,
    'product_type': <product_type>,
    'username': <username>,
    'password': <pasword>
}

downloader = DownloaderFactory.get_downloader('<downloader_type>', '<platform>', **kwargs)

## Download data

# Define coordinates for sub-setting
sel_dict = {
    'time': slice('2023-11-24T010:30:00', '2023-11-25T10:30:00'),
    'latitude': slice(51.5, 52.5),
    'longitude': slice(7, 8)
}
parameters = ['<param>']

xarray_dataset = downloader.download(parameters=parameters, sel_dict=sel_dict)
```

#### Sub-setting

Conventions
- Coordinates are named "latitude" and "longitude", independently of the name in the original file/dataset
- Latitude is defined from -90° to 90°
- Longitude is defined from -180° to 180°

The sub-setting logic is implemented using xarray. Depending on the arguments provided to the `download`-method a different xarray method is used (`sel`, `isel` or `interp`). Note also that `kwargs` are passed on to the corresponding xarray method. For a detailed documentation of sub-setting with xarray check the dedicated section on their website: https://docs.xarray.dev/en/latest/user-guide/indexing.html.

Sub-setting along a trajectory is possible by defining a common dimension (here: 'trajectory') for the sub-setting coordinates:

```python
from datetime import datetime
import xarray

lons = [2.81, 3.19, 4.56, 6.67, 6.68]
lats = [51.9, 53.0, 54.0, 54.3, 55.5]

times = [datetime.strptime("2023-09-20 09:00:00", '%Y-%m-%d %H:%M:%S'),
         datetime.strptime("2023-09-20 11:00:00", '%Y-%m-%d %H:%M:%S'),
         datetime.strptime("2023-09-20 13:00:00", '%Y-%m-%d %H:%M:%S'),
         datetime.strptime("2023-09-20 15:00:00", '%Y-%m-%d %H:%M:%S'),
         datetime.strptime("2023-09-20 17:00:00", '%Y-%m-%d %H:%M:%S')]

lons_xr = xarray.DataArray(lons, dims=['trajectory'])
lats_xr = xarray.DataArray(lats, dims=['trajectory'])
times_xr = xarray.DataArray(times, dims=['trajectory'])
sel_dict = {
    'time': times_xr,
    'longitude': lons_xr,
    'latitude': lats_xr
}
```
To get the settings for the ERA5 CDSapi go to [their website](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=form) 
and select the parameters, time and extent you like to use and click on `show API request` at the bottom of the page.
<br>
You want to copy the dictionary within the request as your settings!
### Available datasets/downloader

| Platform/Provider | Downloader type | Type of data         | Product                                  | Product type | References |
|-------------------|-----------------|----------------------|------------------------------------------|--------------|------------|
| cmems¹            | opendap         | Ocean waves          | cmems_mod_glo_wav_anfc_0.083deg_PT3H-i²  | nrt³         | [1]        |
| cmems¹            | opendap         | Ocean currents       | cmems_mod_glo_phy_anfc_merged-uv_PT1H-i² | nrt³         | [2]        |
| cmems¹            | opendap         | Ocean physics        | cmems_mod_glo_phy_anfc_0.083deg_PT1H-m²  | nrt³         | [2]        |
| gfs               | opendap         | Weather/Atmosphere   | -                                        | -            | [3]        |
| etoponcei         | opendap         | Topology/Bathymetric | -                                        | -            | [4]        |
| era5¹⁴            | cdsapi          | Atmosphere/Ocean     | -                                        | -            | [5]        |


¹Registration needed  
²Check the CMEMS product catalog for additional products: https://data.marine.copernicus.eu/products  
³nrt = near real-time  
⁴The download interface differs from the interface of the 'opendap' downloader type (ToDo: harmonize)

Dataset references:
- [1] https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_WAV_001_027/description
- [2] https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_PHY_001_024/description
- [3] https://thredds.ucar.edu/thredds/catalog/grib/NCEP/GFS/Global_0p25deg/catalog.html
- [4] https://www.ncei.noaa.gov/products/etopo-global-relief-model
- [5] https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels