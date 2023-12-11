import cdsapi

import xarray as xr
import io
import requests

import logging

from maridatadownloader.base import DownloaderBase

logger = logging.getLogger(__name__)







class DownloaderERA5cds(DownloaderBase):
    """
    ERA5 Reanalysis Downloader from cds copernicus based on xarray

     https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=overview
    """
    def __init__(self, uuid, api_key, **kwargs):
        super().__init__('cds', username=uuid, password=api_key, **kwargs)

    def postprocessing(self, dataset, **kwargs):
        """
        ERA5 data come in ranges from 90 to -90 for latitude and from 0 to 360 for longitude.
        Convert dataset globally to ranges (-90, 90) for latitude and (-180, 180) for longitude first
        to make requests across meridian easier to handle.
        """
        attrs_lon = dataset.longitude.attrs
        dataset = dataset.reindex(latitude=list(reversed(dataset.latitude)))
        dataset = dataset.assign_coords(
            longitude=(((dataset.longitude + 180) % 360) - 180))
        dataset.longitude.attrs = attrs_lon
        dataset = dataset.sortby('longitude')
        return dataset

    def download(self, settings=None, outfile=None, **kwargs):
        #force some parameters
        settings['product_type'] = 'reanalysis'
        settings['format'] = 'netcdf'
        client = cdsapi.Client(url='https://cds.climate.copernicus.eu/api/v2', key=f'{self.username}:{self.password}')
        request = client.retrieve(name='reanalysis-era5-single-levels', request=settings)
        r = requests.get(request.location)
        if r.status_code == 200:
            logger.info('download successful')
        nc_data = io.BytesIO(r.content)
        ds = xr.open_dataset(nc_data)
        logger.info('data read successful')
        ds = self.postprocessing(ds)

        if outfile:
            logger.info(f"Save dataset to '{outfile}'")
            ds.to_netcdf(outfile)
        return ds
