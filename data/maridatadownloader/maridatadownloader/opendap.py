import logging
import os
from datetime import datetime, timezone, timedelta, time

# import dask
import xarray
from pydap.client import open_url
from pydap.cas.get_cookies import setup_session
from xarray.backends import NetCDF4DataStore

from maridatadownloader.base import DownloaderBase

logger = logging.getLogger(__name__)

# Currently only OPeNDAP is supported, however, the considered data providers CMEMS and GFS (NCEI) offer further
# data access mechanisms like FTP, WCS (Web Coverage Service) or NCSS (NetCDF Subset Service).


class DownloaderOpendap(DownloaderBase):
    """OPeNDAP downloader class"""

    def __init__(self, platform, username=None, password=None, **kwargs):
        super().__init__('opendap', username=username, password=password, **kwargs)
        self.platform = platform
        self.dataset = None
        self.filename_or_obj = self.get_filename_or_obj(**kwargs)
        self.open_dataset()

    def check_connection(self):
        try:
            self.dataset.info()
            return True
        except Exception:
            return False

    def download(self, parameters=None, sel_dict=None, isel_dict=None, file_out=None, **kwargs):
        """
        :param sel_dict: dict
            value selection, e.g. {'longitude': slice(10.25, 20.75)} or {'longitude': 10.25}
        :param isel_dict: dict
            index selection e.g. {'longitude': slice(0, 10)} or {'longitude': 0}
        :param parameters: str or list
        :param file_out:
        :param args:
        :param kwargs:
        :return: xarray.Dataset

        References:
         - https://docs.xarray.dev/en/stable/user-guide/indexing.html
        """
        # ToDo: add implicit resampling?
        if sel_dict:
            assert not isel_dict, "sel_dict and isel_dict are mutually exclusive"
        if isel_dict:
            assert not sel_dict, "sel_dict and isel_dict are mutually exclusive"

        try:
            dataset = self._preprocessing(parameters=parameters, sel_dict=sel_dict, isel_dict=isel_dict)
        except NotImplementedError:
            dataset = self.dataset

        # Parameter and coordinate subsetting
        if parameters:
            if sel_dict:
                # Check if the selection keys are valid coordinate names
                for key in list(sel_dict.keys()):
                    if key not in dataset[parameters].coords:
                        del sel_dict[key]
                dataset_sub = dataset[parameters].sel(**sel_dict)
            elif isel_dict:
                # Check if the selection keys are valid coordinate names
                for key in list(isel_dict.keys()):
                    if key not in dataset[parameters].coords:
                        del isel_dict[key]
                dataset_sub = dataset[parameters].isel(**isel_dict)
            else:
                dataset_sub = dataset[parameters]
        else:
            # all parameters
            if sel_dict:
                # Check if the selection keys are valid coordinate names
                for key in list(sel_dict.keys()):
                    if key not in dataset.coords:
                        del sel_dict[key]
                dataset_sub = dataset.sel(**sel_dict)
            elif isel_dict:
                # Check if the selection keys are valid coordinate names
                for key in list(isel_dict.keys()):
                    if key not in dataset.coords:
                        del isel_dict[key]
                dataset_sub = dataset.isel(**isel_dict)
            else:
                dataset_sub = dataset

        try:
            dataset_sub = self._postprocessing(dataset_sub)
        except NotImplementedError:
            pass

        if file_out:
            logger.info(f"Save dataset to '{file_out}'")
            dataset_sub.to_netcdf(file_out)

        return dataset_sub

    def get_filename_or_obj(self, **kwargs):
        """Should return either the OPeNDAP url, a list of OPeNDAP urls or a DataStore object
        (see https://docs.xarray.dev/en/stable/generated/xarray.open_dataset.html)
        """
        raise NotImplementedError("._get_filename_or_obj() must be overridden.")

    def open_dataset(self):
        if type(self.filename_or_obj) == list:
            self.dataset = xarray.open_mfdataset(self.filename_or_obj)
        else:
            self.dataset = xarray.open_dataset(self.filename_or_obj)
        # ToDO: use cache=False here or in _transform?
        # self.dataset = xarray.open_dataset(self.filename_or_obj, cache=False)

    def release_resources(self):
        """Release resources from dataset using xarray.Dataset.close()"""
        try:
            self.dataset.close()
        except Exception:
            logger.warning("Could not release resources for dataset.")

    def set_filename_or_obj(self, filename_or_obj=None):
        if filename_or_obj:
            self.filename_or_obj = filename_or_obj
        else:
            self.filename_or_obj = self.get_filename_or_obj()
        self.open_dataset()

    def _preprocessing(self, parameters=None, sel_dict=None, isel_dict=None):
        """Apply operations on the xarray.Dataset before download, e.g. transform coordinates"""
        raise NotImplementedError("._preprocessing() can optionally be overridden.")

    def _postprocessing(self, dataset):
        """Apply operations on the xarray.Dataset after download, e.g. rename variables"""
        raise NotImplementedError("._postprocessing() can optionally be overridden.")


class DownloaderOpendapGFS(DownloaderOpendap):
    """
    OPeNDAP downloader class for the Global Forecast System (GFS)

    By default, this class provides access to the GFS weather forecast data (-2 days up to +16 days).
    If access to archived forecast data is desired, the user must provide a time window (e.g., {'time': ('2023-05-01T00:00:00', '2023-05-02T12:00:00')}) when instantiating the class.

    References:
     - https://www.emc.ncep.noaa.gov/emc/pages/numerical_forecast_systems/gfs.php
    """

    def __init__(self, username=None, password=None, **kwargs):
        self.model_cycles = [time(0), time(6), time(12), time(18)]
        self.forecast_times = [time(0), time(3), time(6), time(9), time(12), time(15), time(18), time(21)]
        super().__init__('gfs', username=username, password=password, **kwargs)

    def download(self, parameters=None, sel_dict=None, isel_dict=None, file_out=None, **kwargs):
        if sel_dict:
            if 'time' in sel_dict:
                time = sel_dict['time']
            elif 'time1' in sel_dict:
                time = sel_dict['time1']
            elif 'time2' in kwargs:
                time = sel_dict['time2']
            else:
                time = None
            if time:
                assert type(time) == slice, "'time' has to be a slice object"
                try:
                    time_start = datetime.strptime(time.start, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
                    time_end = datetime.strptime(time.stop, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
                except Exception as err:
                    print(f"Unexpected {err=}, {type(err)=}")
                    raise
                assert time_start <= time_end, "Start time must be smaller than end time"
                if time_end < (datetime.now(timezone.utc) - timedelta(days=3)):
                    print("Access archived GFS data")
                    return self._download_archived_data(time_start, time_end, parameters=parameters,
                                                        sel_dict=sel_dict, isel_dict=isel_dict,
                                                        file_out=file_out, **kwargs)
                else:
                    return super().download(parameters=parameters, sel_dict=sel_dict,
                                            isel_dict=isel_dict, file_out=file_out, **kwargs)
        else:
            return super().download(parameters=parameters, sel_dict=sel_dict, isel_dict=isel_dict,
                                    file_out=file_out, **kwargs)

    def get_filename_or_obj(self, **kwargs):
        return 'https://thredds.ucar.edu/thredds/dodsC/grib/NCEP/GFS/Global_0p25deg/Best'

    def _download_archived_data(self, time_start, time_end, parameters=None, sel_dict=None, isel_dict=None,
                                file_out=None, **kwargs):
        self.urls = self._get_urls_time_window(time_start, time_end)
        self.datasets = []
        for url in self.urls:
            self.set_filename_or_obj(url)
            dataset_temp = super().download(parameters=parameters, sel_dict=sel_dict, isel_dict=isel_dict,
                                            file_out=None, **kwargs)
            self.datasets.append(dataset_temp)
        dataset_merged = self._merge_datasets(self.datasets)
        # Reset self.filename_or_obj in case actual forecasts are downloaded later
        self.set_filename_or_obj()
        if file_out:
            logger.info(f"Save dataset to '{file_out}'")
            dataset_merged.to_netcdf(file_out)
        return dataset_merged

    def _get_url(self, datetime_obj):
        """E.g. https://rda.ucar.edu/thredds/dodsC/files/g/ds084.1/2023/20230501/gfs.0p25.2023050100.f000.grib2"""
        year = f'{datetime_obj.year}'
        month = f'{datetime_obj.month:02d}'
        day = f'{datetime_obj.day:02d}'
        if datetime_obj.time() in self.model_cycles:
            hour = f'{datetime_obj.hour:02d}'
            forecast_time = 'f000'
        elif datetime_obj.time() in self.forecast_times and datetime_obj.hour == 3:
            hour = '00'
            forecast_time = 'f003'
        elif datetime_obj.time() in self.forecast_times and datetime_obj.hour == 9:
            hour = '06'
            forecast_time = 'f003'
        elif datetime_obj.time() in self.forecast_times and datetime_obj.hour == 15:
            hour = '12'
            forecast_time = 'f003'
        elif datetime_obj.time() in self.forecast_times and datetime_obj.hour == 21:
            hour = '18'
            forecast_time = 'f003'
        else:
            raise Exception()
        url = 'https://rda.ucar.edu/thredds/dodsC/files/g/ds084.1/' + \
              year + '/' + year + month + day + '/' + 'gfs.0p25.' + \
              year + month + day + hour + '.' + forecast_time + '.grib2'
        return url

    def _get_urls_time_window(self, time_start, time_end):
        l = [element for element in self.forecast_times if element <= time_start.time()]
        if l:
            closest_smaller_gfs_datetime = datetime.combine(time_start.date(), max(l), tzinfo=timezone.utc)
        else:
            return []
        urls = []
        for n in range(int((time_end - closest_smaller_gfs_datetime) / timedelta(hours=3)) + 1):
            time_tmp = closest_smaller_gfs_datetime + n * timedelta(hours=3)
            urls.append(self._get_url(time_tmp))
        return urls

    def _merge_datasets(self, datasets):
        # for dataset in datasets:
        dataset_merged = xarray.concat(datasets, dim="time")
        return dataset_merged

    def _preprocessing(self, parameters=None, sel_dict=None, isel_dict=None):
        """
        GFS (forecast) data come in ranges from 90 to -90 for latitude and from 0 to 360 for longitude.
        Convert dataset globally to ranges (-90, 90) for latitude and (-180, 180) for longitude first
        to make requests across meridian easier to handle.
        """
        dataset_transformed = self.dataset
        dataset_transformed = dataset_transformed.rename({'lat': 'latitude'})
        dataset_transformed = dataset_transformed.rename({'lon': 'longitude'})
        attrs_lon = dataset_transformed.longitude.attrs
        dataset_transformed = dataset_transformed.reindex(latitude=list(reversed(dataset_transformed.latitude)))
        dataset_transformed = dataset_transformed.assign_coords(
            longitude=(((dataset_transformed.longitude + 180) % 360) - 180))
        dataset_transformed.longitude.attrs = attrs_lon
        dataset_transformed = dataset_transformed.sortby('longitude')
        return dataset_transformed

    def _postprocessing(self, dataset):
        """
        It seems that for the same parameters sometimes coordinate 'time' is used, and sometimes 'time1' ...
        """
        if 'time1' in dataset.coords and 'time' not in dataset.coords:
            dataset = dataset.rename({'time1': 'time', 'reftime1': 'reftime'})
        if 'height_above_ground2' in dataset.coords and 'height_above_ground' not in dataset.coords:
            dataset = dataset.rename({'height_above_ground2': 'height_above_ground'})
        if 'reftime' in dataset.coords:
            dataset = dataset.drop('reftime')
        return dataset


class DownloaderOpendapCMEMS(DownloaderOpendap):
    """
    OPeNDAP downloader class for CMEMS

    References:
        -  https://help.marine.copernicus.eu/en/articles/5182598-how-to-consume-the-opendap-api-and-cas-sso-using-python
    """

    def __init__(self, product, product_type, username, password, **kwargs):
        """
        :param product: str
        :param product_type: str
            'my' (multi year) or 'nrt' (near real time)
        :param username:
        :param password:
        :param kwargs:
        """
        self.product = product
        self.product_type = product_type
        super().__init__('cmems', username=username, password=password, **kwargs)

    def get_filename_or_obj(self, **kwargs):
        assert self.product
        assert self.product_type
        cas_url = 'https://cmems-cas.cls.fr/cas/login'
        session = setup_session(cas_url, self.username, self.password)
        session.cookies.set("CASTGC", session.cookies.get_dict()['CASTGC'])
        url = f'https://{self.product_type}.cmems-du.eu/thredds/dodsC/{self.product}'
        try:
            # NetCDF4DataStore also supports OpenDAP
            data_store = xarray.backends.PydapDataStore(open_url(url, session=session))
        except Exception as err:
            raise err
        return data_store

    def set_product(self, product, product_type='nrt'):
        self.product = product
        self.product_type = product_type
        self.filename_or_obj = self.get_filename_or_obj()
        self.open_dataset()
