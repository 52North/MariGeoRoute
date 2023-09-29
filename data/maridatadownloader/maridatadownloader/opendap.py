import logging
from copy import deepcopy
from datetime import datetime, timezone, timedelta, time
from math import ceil

# import dask
import xarray
from numpy import datetime64, ndarray
from pydap.client import open_url
from pydap.cas.get_cookies import setup_session
from xarray.backends import NetCDF4DataStore

from maridatadownloader.base import DownloaderBase
from maridatadownloader.utils import convert_datetime, parse_datetime

logger = logging.getLogger(__name__)


# Currently only OPeNDAP is supported, however, the considered data providers CMEMS and GFS (NCEI) offer further
# data access mechanisms like FTP, WCS (Web Coverage Service) or NCSS (NetCDF Subset Service).


class DownloaderOpendap(DownloaderBase):
    """
    OPeNDAP downloader class based on xarray

    The download method provides a convenient way to download data via an OPeNDAP connection including some checks
    to add robustness and the possibility to apply preprocessing and postprocessing.
    If it doesn't suit the requirements of the use case, it is also possible to directly work on the xarray.Dataset
    (self.dataset) and use all the methods provided by xarray directly
    (https://docs.xarray.dev/en/latest/generated/xarray.Dataset.html#xarray.Dataset).

    Coordinate subsetting with xarray can be done in different ways, e.g.:
     - by value or by index
     - allowing only exact matches or inexact matches (including different methods for inexact matches)
     - allowing off-grid subsetting using interpolation (including different interpolation methods)
    The download method can be used in all the aforementioned ways. For details check the method documentation.
    """

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

    def download(self, parameters=None, sel_dict=None, isel_dict=None, file_out=None, interpolate=False, **kwargs):
        """
        :param parameters: str or list
        :param sel_dict: dict
            Coordinate selection by value, e.g. {'longitude': slice(10.25, 20.75)} or {'longitude': 10.25}
        :param isel_dict: dict
            Coordinate selection by index e.g. {'longitude': slice(0, 10)} or {'longitude': 0}
        :param file_out:
            File name used to save the dataset as NetCDF file. No file is saved without specifying file_out
        :param interpolate: bool
            Set to True if data should be downloaded off-grid so that interpolation is applied. Note that the
            sel method supports inexact matches but doesn't support actual interpolation (off-grid values).
        :param kwargs:
            Additional keyword arguments are passed to the corresponding method sel, isel or interp.
            For details on which arguments can be used check the references below.
        :return: xarray.Dataset

        References:
         - https://docs.xarray.dev/en/stable/user-guide/indexing.html
         - https://docs.xarray.dev/en/latest/generated/xarray.Dataset.sel.html
         - https://docs.xarray.dev/en/latest/generated/xarray.Dataset.isel.html
         - https://docs.xarray.dev/en/latest/user-guide/interpolation.html
         - https://docs.xarray.dev/en/latest/generated/xarray.Dataset.interp.html
        """
        coord_dict, method = self._prepare_download(sel_dict, isel_dict, interpolate)

        try:
            dataset = self.preprocessing(self.dataset, parameters=parameters, coord_dict=coord_dict)
        except NotImplementedError:
            dataset = self.dataset

        dataset_sub = self._apply_subsetting(dataset, parameters, coord_dict, method, **kwargs)

        try:
            dataset_sub = self.postprocessing(dataset_sub)
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
            self.dataset = xarray.open_mfdataset(self.filename_or_obj, decode_coords="all")
        else:
            self.dataset = xarray.open_dataset(self.filename_or_obj, decode_coords="all")
            # ToDO: use cache=False here or in preprocessing?
            # self.dataset = xarray.open_dataset(self.filename_or_obj, cache=False)

    def postprocessing(self, dataset):
        """Apply operations on the xarray.Dataset after download, e.g. rename variables"""
        raise NotImplementedError(".postprocessing() can optionally be overridden.")

    def preprocessing(self, dataset, parameters=None, coord_dict=None):
        """Apply operations on the xarray.Dataset before download, e.g. transform coordinates"""
        raise NotImplementedError(".preprocessing() can optionally be overridden.")

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

    def _apply_subsetting(self, dataset, parameters=None, coord_dict=None, method=None, **kwargs):
        # Apply parameter subsetting
        if parameters:
            dataset_sub = dataset[parameters]
        else:
            dataset_sub = dataset

        # Check if the selection keys are valid dimension names
        if coord_dict:
            for key in list(coord_dict.keys()):
                if key not in dataset_sub.dims:
                    del coord_dict[key]

        # Apply coordinate subsetting
        if method == 'sel':
            dataset_sub = dataset_sub.sel(**coord_dict, **kwargs)
        elif method == 'isel':
            dataset_sub = dataset_sub.isel(**coord_dict, **kwargs)
        elif method == 'interp':
            dataset_sub = dataset_sub.interp(**coord_dict, **kwargs)

        return dataset_sub

    def _prepare_download(self, sel_dict=None, isel_dict=None, interpolate=False):
        # Make a copy of the sel/isel dict because key-value pairs might be deleted from it
        coord_dict = {}
        method = None
        if sel_dict:
            assert not isel_dict, "sel_dict and isel_dict are mutually exclusive"
            coord_dict = deepcopy(sel_dict)
            method = 'sel'
        if isel_dict:
            assert not sel_dict, "sel_dict and isel_dict are mutually exclusive"
            coord_dict = deepcopy(isel_dict)
            method = 'isel'
        if interpolate:
            assert not isel_dict, "interpolation cannot be applied with index subsetting"
            method = 'interp'
        return coord_dict, method


class DownloaderOpendapGFS(DownloaderOpendap):
    """
    OPeNDAP downloader class for the Global Forecast System (GFS)

    By default, this class provides access to the GFS weather forecast data (-2 days up to +16 days).
    If access to archived forecast data is desired, the user must provide a time window (e.g., {'time': (
    '2023-05-01T00:00:00', '2023-05-02T12:00:00')}) when instantiating the class.

    References:
     - https://www.emc.ncep.noaa.gov/emc/pages/numerical_forecast_systems/gfs.php
    """

    def __init__(self, username=None, password=None, **kwargs):
        self.model_cycles = [time(0), time(6), time(12), time(18)]
        self.forecast_times = [time(0), time(3), time(6), time(9), time(12), time(15), time(18), time(21)]
        super().__init__('gfs', username=username, password=password, **kwargs)

    def download(self, parameters=None, sel_dict=None, isel_dict=None, file_out=None, interpolate=False, **kwargs):
        # Note: we do not support index selection (isel_dict) for archived GFS data by choice
        # FIXME: if multiple time coordinates (time, time1, ...) are provided, should we extract the longest overall
        #        time interval?
        if sel_dict and not isel_dict:
            if 'time' in sel_dict:
                time_ = sel_dict['time']
            elif 'time1' in sel_dict:
                time_ = sel_dict['time1']
            elif 'time2' in sel_dict:
                time_ = sel_dict['time2']
            else:
                time_ = None
            if time_ is not None:
                # Note: xarray doesn't support tuples as indexer
                # FIXME: make sure time_start and time_end are timezone aware (because of "<"-comparison)
                if type(time_) == str:
                    time_start = time_end = parse_datetime(time_)
                elif type(time_) == datetime:
                    time_start = time_end = time_
                elif type(time_) == slice:
                    time_start = time_.start
                    time_end = time_.stop
                    if type(time_start) == str:
                        time_start = parse_datetime(time_start)
                    if type(time_end) == str:
                        time_end = parse_datetime(time_end)
                elif type(time_) == list or type(time_) == ndarray:
                    time_start = min(time_)
                    time_end = max(time_)
                    if type(time_start) == str:
                        time_start = parse_datetime(time_start)
                    if type(time_end) == str:
                        time_end = parse_datetime(time_end)
                elif type(time_) == xarray.DataArray:
                    time_start = min(time_).values
                    time_end = max(time_).values
                    if type(time_start) == ndarray:
                        time_start = parse_datetime(time_start.item())
                    if type(time_end) == ndarray:
                        time_end = parse_datetime(time_end.item())
                    if type(time_start) == datetime64:
                        time_start = convert_datetime(time_start)
                    if type(time_end) == datetime64:
                        time_end = convert_datetime(time_end)
                else:
                    raise ValueError(f"Unsupported indexer type '{type(time_)}'")
                assert time_start <= time_end, "Start time must be smaller or equal to end time"
                if time_end < (datetime.now(timezone.utc) - timedelta(days=3)):
                    print("Access archived GFS data")
                    return self._download_archived_data(time_start, time_end, parameters, sel_dict, file_out,
                                                        interpolate, **kwargs)
        return super().download(parameters, sel_dict, isel_dict, file_out, interpolate, **kwargs)

    def get_filename_or_obj(self, **kwargs):
        return 'https://thredds.ucar.edu/thredds/dodsC/grib/NCEP/GFS/Global_0p25deg/Best'

    def preprocessing(self, dataset, parameters=None, coord_dict=None):
        """
        GFS (forecast) data come in ranges from 90 to -90 for latitude and from 0 to 360 for longitude.
        Convert dataset globally to ranges (-90, 90) for latitude and (-180, 180) for longitude first
        to make requests across meridian easier to handle.
        """
        if parameters:
            dataset = dataset[parameters]
        dataset = dataset.rename({'lat': 'latitude'})
        dataset = dataset.rename({'lon': 'longitude'})
        attrs_lon = dataset.longitude.attrs
        dataset = dataset.reindex(latitude=list(reversed(dataset.latitude)))
        dataset = dataset.assign_coords(
            longitude=(((dataset.longitude + 180) % 360) - 180))
        dataset.longitude.attrs = attrs_lon
        dataset = dataset.sortby('longitude')
        return dataset

    def postprocessing(self, dataset):
        """
        It seems that for the same parameters sometimes coordinate 'time' is used, and sometimes 'time1' ...
        """
        if 'time1' in dataset.coords and 'time' not in dataset.coords:
            dataset = dataset.rename({'time1': 'time'})
        if 'time2' in dataset.coords and 'time' not in dataset.coords:
            dataset = dataset.rename({'time2': 'time'})
        if 'reftime1' in dataset.coords and 'reftime' not in dataset.coords:
            dataset = dataset.rename({'reftime1': 'reftime'})
        if 'reftime2' in dataset.coords and 'reftime' not in dataset.coords:
            dataset = dataset.rename({'reftime2': 'reftime'})
        if 'height_above_ground1' in dataset.coords and 'height_above_ground' not in dataset.coords:
            dataset = dataset.rename({'height_above_ground1': 'height_above_ground'})
        if 'height_above_ground2' in dataset.coords and 'height_above_ground' not in dataset.coords:
            dataset = dataset.rename({'height_above_ground2': 'height_above_ground'})
        return dataset

    def _download_archived_data(self, time_start, time_end, parameters=None, sel_dict={}, file_out=None,
                                interpolate=False, **kwargs):
        # Merge datasets from different urls
        self.urls = self._get_urls_time_window(time_start, time_end)
        datasets = []
        for url in self.urls:
            dataset_temp = xarray.open_dataset(url)
            dataset_temp = self.preprocessing(dataset_temp, parameters)
            dataset_temp = self.postprocessing(dataset_temp)
            # Is there a significant speed-up if we apply additional subsetting already here?
            # dataset_temp = self.postprocessing(dataset_temp).isel(height_above_ground=0)
            datasets.append(dataset_temp)
        dataset = xarray.concat(datasets, dim="time")

        # Because of possible coordinate renaming in self.postprocessing, we need to make sure that the original
        # indexers are considered in the subsequent subsetting process
        if 'time1' in sel_dict and 'time' not in sel_dict:
            sel_dict['time'] = sel_dict['time1']
        if 'time2' in sel_dict and 'time' not in sel_dict:
            sel_dict['time'] = sel_dict['time2']
        if 'reftime1' in sel_dict and 'reftime' not in sel_dict:
            sel_dict['reftime'] = sel_dict['reftime1']
        if 'reftime2' in sel_dict and 'reftime' not in sel_dict:
            sel_dict['reftime'] = sel_dict['reftime2']
        if 'height_above_ground1' in sel_dict and 'height_above_ground' not in sel_dict:
            sel_dict['height_above_ground'] = sel_dict['height_above_ground1']
        if 'height_above_ground2' in sel_dict and 'height_above_ground' not in sel_dict:
            sel_dict['height_above_ground'] = sel_dict['height_above_ground2']

        # Download
        coord_dict, method = self._prepare_download(sel_dict, interpolate=interpolate)
        dataset_sub = self._apply_subsetting(dataset, parameters, coord_dict, method, **kwargs)

        if file_out:
            logger.info(f"Save dataset to '{file_out}'")
            dataset_sub.to_netcdf(file_out)

        return dataset_sub

    def _get_url(self, datetime_obj):
        """E.g. https://thredds.rda.ucar.edu/thredds/catalog/dodsC/files/g/ds084.1/2023/20230501/gfs.0p25.2023050100
        .f000.grib2"""
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
        url = ('https://thredds.rda.ucar.edu/thredds/dodsC/files/g/ds084.1/' + year + '/' + year + month + day + '/' +
               'gfs.0p25.' + year + month + day + hour + '.' + forecast_time + '.grib2')
        return url

    def _get_urls_time_window(self, time_start, time_end):
        l = [element for element in self.forecast_times if element <= time_start.time()]
        if l:
            closest_smaller_gfs_datetime = datetime.combine(time_start.date(), max(l), tzinfo=timezone.utc)
        else:
            return []
        urls = []
        for n in range(ceil((time_end - closest_smaller_gfs_datetime) / timedelta(hours=3)) + 1):
            time_tmp = closest_smaller_gfs_datetime + n * timedelta(hours=3)
            urls.append(self._get_url(time_tmp))
        return urls


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


class DownloaderOpendapETOPONCEI(DownloaderOpendap):
    """
    OPeNDAP downloader class for topology and bathymetric data from NCEI

    References:
        -  https://www.ngdc.noaa.gov/thredds/catalog/global/ETOPO2022/30s/30s_bed_elev_netcdf/catalog.html?dataset
        =globalDatasetScan/ETOPO2022/30s/30s_bed_elev_netcdf/ETOPO_2022_v1_30s_N90W180_bed.nc
    """

    def __init__(self, **kwargs):
        """
        :param kwargs:
        """
        super().__init__('etoponcei', **kwargs)

    def get_filename_or_obj(self, **kwargs):
        url = ('https://www.ngdc.noaa.gov/thredds/dodsC/global/ETOPO2022/30s/30s_bed_elev_netcdf'
               '/ETOPO_2022_v1_30s_N90W180_bed.nc')
        return url
