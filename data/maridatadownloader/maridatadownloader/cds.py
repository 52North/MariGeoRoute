import io
import logging

import cdsapi
import requests
import xarray as xr

from maridatadownloader.base import DownloaderBase

logger = logging.getLogger(__name__)


class DownloaderCdsapiERA5(DownloaderBase):
    """
    ERA5 Reanalysis Downloader from cds copernicus based on xarray

    https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels
    """
    def __init__(self, uuid, api_key, **kwargs):
        super().__init__('cdsapi', username=uuid, password=api_key, **kwargs)
        self.platform = 'era5'
        self.dataset = None
        self.url = 'https://cds.climate.copernicus.eu/api/v2'
        self.client = cdsapi.Client(url=self.url, key=f'{self.username}:{self.password}')

    def download(self, settings=None, file_out=None, **kwargs):
        """
        :param settings:
        :param file_out:
        :param kwargs:
        :return: xarray.Dataset
        """
        settings['product_type'] = 'reanalysis'
        settings['format'] = 'netcdf'
        request = self.client.retrieve(name='reanalysis-era5-single-levels', request=settings)
        r = requests.get(request.location)
        if r.status_code == 200:
            logger.info('Download successful')
        nc_data = io.BytesIO(r.content)
        self.dataset = xr.open_dataset(nc_data)
        logger.info('Data read successful')

        try:
            dataset = self.postprocessing(self.dataset)
        except NotImplementedError:
            pass

        if file_out:
            logger.info(f"Save dataset to '{file_out}'")
            dataset.to_netcdf(file_out)
        return dataset

    def postprocessing(self, dataset, **kwargs):
        """
        ERA5 data come in ranges from 90 to -90 for latitude. Convert dataset globally to ranges (-90, 90) for latitude.
        """
        dataset = dataset.reindex(latitude=list(reversed(dataset.latitude)))
        return dataset
