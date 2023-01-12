"""Weather functions."""
import numpy as np
import datetime as dt
import xarray as xr
import bbox as bbox
import matplotlib
from bbox import BBox2D, XYXY
import sys

import pygrib as pg

from scipy.interpolate import RegularGridInterpolator

import utils
from utils import round_time


class WeatherCond():
    model: str
    time_steps: int
    time_res: dt.timedelta
    time_start: dt.datetime
    time_end: dt.timedelta
    map_size: bbox.BBox2D
    ds: xr.Dataset
    wind_functions: None
    wind_vectors: None

    def __init__(self, filepath, model, time, hours, time_res):
        utils.print_line()
        print('Initialising weather')

        self.read_dataset(filepath)

        self.model = model
        self.time_res = time_res
        self.time_start = time
        self.time_end = time + dt.timedelta(hours=hours)

        time_passed = self.time_end - self.time_start
        self.time_steps = int(time_passed.total_seconds()/self.time_res.total_seconds())

        print('forecast from ' + str(self.time_start) + ' to ' + str(self.time_end))
        print('nof time steps', self.time_steps)
        utils.print_line()

    def close_env_file(self):
        self.ds.close()

    def adjust_depth_format(self, depth_path):
        debug = True
        ds_depth = xr.open_dataset(depth_path)
        ds_depth = ds_depth.sortby("latitude")
        ds_depth.load()
        ds_depth_pos = ds_depth.where(ds_depth.longitude <= 180, drop=True)
        ds_depth_neg = ds_depth.where(ds_depth.longitude > 180, drop=True)
        ds_depth_neg['longitude'] = ds_depth_neg['longitude'] - 360
        ds_depth = ds_depth_pos.merge(ds_depth_neg)

        if(debug):
            print('ds_depth_pos', ds_depth_pos)
            print('ds_depth_neg', ds_depth_neg)
            print('ds_depth new', ds_depth)

        return ds_depth

    def add_depth_to_EnvData(self, depth_path):
        try:
            lat_start = self.map_size.x1
            lat_end = self.map_size.x2
            lon_start = self.map_size.y1
            lon_end = self.map_size.y2
        except:
            raise Exception('Need to initialise weather data bounding box before adding depth data!')

        ds_depth = xr.open_dataset(depth_path)
        ds_depth = ds_depth.where((ds_depth.lat > lat_start) & (ds_depth.lat < lat_end) & (ds_depth.lon > lon_start) & (
                    ds_depth.lon < lon_end) & (ds_depth.z < 0), drop=True)

        #depth_lat = ds_depth['latitude'].to_numpy()
        #depth_lon = ds_depth['longitude'].to_numpy()

        #lat_int = np.intersect1d(ds_lat, depth_lat)
        #lon_int = np.intersect1d(ds_lon, depth_lon)
        #np.set_printoptions(threshold=sys.maxsize)
        #print('lat_int', lat_int)
        #print('ds_lat', ds_lat)
        #print('depth_lat', depth_lat)
        #print('lon_int', lon_int)
        #print('ds_lon', ds_lon)
        #print('depth_lon', depth_lon)

        #print("sorted", ds_depth)
        #ds_depth.load()

        ds_depth = ds_depth.rename(lat="latitude", lon="longitude")
        weather_int = self.ds.interp_like(ds_depth, method="linear")   

        depth = ds_depth['z'].to_numpy()
        depth = np.nan_to_num(depth)

        weather_int['depth'] = (['latitude', 'longitude'], depth)
        depth_test = weather_int['depth'].to_numpy()
        if(np.isnan(depth_test).any()):
            print('depth_test:', depth_test)
            raise Exception('element of depth is nan!')
        self.ds = weather_int

    @property
    def time_res(self):
        return self._time_res

    @time_res.setter
    def time_res(self, value):
        if (value < 3): raise ValueError('Resolution below 3h not possible')
        self._time_res = dt.timedelta(hours=value)
        print('time resolution: ' + str(self._time_res) + ' hours')

    @property
    def time_start(self):
        return self._time_start

    @time_start.setter
    def time_start(self,value):
        rounded_time = value - self.time_res/2
        rounded_time = round_time(rounded_time, int(self.time_res.total_seconds()))
        self._time_start = rounded_time

    @property
    def time_end(self):
        return self._time_end

    @time_end.setter
    def time_end(self, value):
        rounded_time = value + self.time_res / 2
        rounded_time = round_time(rounded_time, int(self.time_res.total_seconds()))
        self._time_end = rounded_time

    def get_time_step_index(self, time):
        rounded_time = round_time(time, int(self.time_res.total_seconds()))
        time_passed = rounded_time - self.time_start
        idx = (time_passed.total_seconds() / self.time_res.total_seconds())
        return {'rounded_time' : rounded_time, 'idx' : idx}

    def set_map_size(self, lat1, lon1, lat2, lon2):
        self.map_size=BBox2D([lat1, lon1, lat2, lon2], mode=XYXY)

    def get_map_size(self):
        return self.map_size

    def read_dataset(self, filepath):
        print('Reading dataset from', filepath)
        self.ds = xr.open_dataset(filepath)
        print(self.ds)

    def check_ds_format(self):
        print('Printing dataset', self.ds)
    '''
    def grib_to_wind_function(filepath):
        """Vectorized wind functions from grib file.GRIB is a file format for the storage and transport of gridded meteorological data,
        such as Numerical Weather Prediction model output."""
        grbs = pg.open(filepath)

        u, _, _ = grbs[1].data()
        v, _, _ = grbs[2].data()

        tws = np.sqrt(u * u + v * v)
        twa = 180.0 / np.pi * np.arctan2(u, v) + 180.0

        return {'twa': twa, 'tws': tws}     
    '''



    '''
    def grib_to_wind_vectors(filepath, lat1, lon1, lat2, lon2):
        """Return u-v components for given rect for visualization."""
        grbs = pg.open(filepath)
        u, lats_u, lons_u = grbs[1].data(lat1, lat2, lon1, lon2)
        v, lats_v, lons_v = grbs[2].data(lat1, lat2, lon1, lon2)
        return u, v, lats_u, lons_u
    '''

    def get_twatws_from_uv(self, u, v):
        tws = np.sqrt(u ** 2 + v ** 2)
        twa = 180.0 / np.pi * np.arctan2(u, v) + 180.0  # angle from 0° to 360°, 0° = N
        return twa, tws

    def init_wind_vectors(self):
        """Return wind vectors for given number of hours.
            Parameters:
                    model (dict): available forecast wind functions
                    hours_ahead (int): number of hours looking ahead
                    lats, lons: rectange defining forecast area
            Returns:
                    wind_vectors (dict):
                        model: model timestamp
                        hour: function for given forecast hour
            """

        wind_vectors = {}
        wind_vectors['model'] = self.model

        for i in range(self.time_steps):
            time = self.time_start + self.time_res * i
            wind_vectors[i] = self.read_wind_vectors(time)
            #print('reading wind vector time', time)

        self.wind_vectors = wind_vectors

    def init_wind_functions(self):
        """
        Read wind functions.
            Parameters:
                    model (dict): available forecast wind functions
            Returns:
                    wind_functions (dict):
                        model: model timestamp
                        model+hour: function for given forecast hour
         """
        wind_function = {}
        wind_function['model'] = self.model

        for i in range(self.time_steps):
            wind_function[i] = self.read_wind_functions(i)

        self.wind_functions = wind_function

    def get_wind_function(self, coordinate, time):
        """
        Vectorized TWA and TWS function from forecast.
            Parameters:
                    winds (dict): available forecast wind functions
                    coordinate (array): array of tuples (lats, lons)
                    time (datetime): time to forecast
            Returns:
                    forecast (dict):
                        twa (array): array of TWA
                        tws (array): array of TWS
        """
        debug = True
        time_passed = self.get_time_step_index(time)
        rounded_time= time_passed['rounded_time']
        idx = time_passed['idx']

        try:
            wind_timestamp = self.wind_functions[idx]['timestamp']
        except ValueError:
            print('Requesting weather data for ' + str(time) + ' at index ' + str(idx) + ' but only ' + str(self.time_steps) + ' available')

        if not (rounded_time==self.wind_functions[idx]['timestamp']):
            ex = 'Accessing wrong weather forecast. Accessing element ' + str(self.wind_functions[idx]['timestamp']) + ' but current rounded time is ' + str(rounded_time)
            raise Exception(ex)

        wind = self.wind_functions[idx]
        try:
            twa = wind['twa'](coordinate)
            tws = wind['tws'](coordinate)
        except:
            raise Exception('Running out of weather map!')

        return {'twa': twa, 'tws': tws}

    def get_wind_vector(self, time):
        time_passed = self.get_time_step_index(time)
        rounded_time = time_passed['rounded_time']
        idx = time_passed['idx']

        try:
            wind_timestamp = self.wind_vectors[idx]['timestamp']
        except KeyError:
            print('Requesting weather data for ' + str(time) + ' at index ' + str(idx) + ' but only ' + str(self.time_steps) + ' available')
            raise

        if not (rounded_time == wind_timestamp):
            ex = 'Accessing wrong weather forecast. Accessing element ' + str(
                self.wind_vectors[idx]['timestamp']) + ' but current rounded time is ' + str(rounded_time)
            raise Exception(ex)

        return self.wind_vectors[idx]


class WeatherCondNCEP(WeatherCond):
    def __init__(self, filepath, model, time, hours, time_res):
        WeatherCond.__init__(self, filepath, model, time, hours, time_res)
        print('WARNING: not well maintained. Currently one data file for one particular times is read several times')

    def calculate_wind_function(self):
        """Vectorized wind functions from NetCDF file."""

        twa, tws = self.get_twatws_from_uv(self.ds.u10, self.ds.v10)
        tws = tws.to_numpy()
        twa = twa.to_numpy()

        return {'twa': twa, 'tws': tws}

    def read_wind_functions(self, iTime):
        time = self.time_start + self.time_res*iTime

        wind = self.calculate_wind_function()

        lats_grid = np.linspace(-90, 90, 181)
        lons_grid = np.linspace(0, 360, 361)

        f_twa = RegularGridInterpolator(
            (lats_grid, lons_grid),
            np.flip(np.hstack((wind['twa'], wind['twa'][:, 0].reshape(181, 1))), axis=0),
        )

        f_tws = RegularGridInterpolator(
            (lats_grid, lons_grid),
            np.flip(np.hstack((wind['tws'], wind['tws'][:, 0].reshape(181, 1))), axis=0),
        )

        return {'twa': f_twa, 'tws': f_tws, 'timestamp': time}

    def read_wind_vectors(self, time):
        """Return u-v components for given rect for visualization."""
        lat1 = self.map_size.x1
        lat2 = self.map_size.x2
        lon1 = self.map_size.y1
        lon2 = self.map_size.y2

        u = self.ds['u10'].where(
            (self.ds.latitude >= lat1) & (self.ds.latitude <= lat2) & (self.ds.longitude >= lon1) & (
                    self.ds.longitude <= lon2), drop=True)
        v = self.ds['v10'].where(
            (self.ds.latitude >= lat1) & (self.ds.latitude <= lat2) & (self.ds.longitude >= lon1) & (
                    self.ds.longitude <= lon2), drop=True)
        lats_u_1D = self.ds['latitude'].where((self.ds.latitude >= lat1) & (self.ds.latitude <= lat2), drop=True)
        lons_u_1D = self.ds['longitude'].where((self.ds.longitude >= lon1) & (self.ds.longitude <= lon2), drop=True)

        u = u.to_numpy()
        v = v.to_numpy()
        lats_u_1D = lats_u_1D.to_numpy()
        lons_u_1D = lons_u_1D.to_numpy()
        lats_u = np.tile(lats_u_1D[:, np.newaxis], u.shape[1])
        lons_u = np.tile(lons_u_1D, (u.shape[0], 1))

        return {'u': u,'v': v, 'lats_u': lats_u, 'lons_u': lons_u, 'timestamp': time}

class WeatherCondCMEMS(WeatherCond):
    def calculate_wind_function(self, time):
        time_str=time.strftime('%Y-%m-%d %H:%M:%S')
        #print('Reading time', time_str)

        try:
            u = self.ds['u-component_of_wind_maximum_wind'].sel(time=time_str)
            v = self.ds['v-component_of_wind_maximum_wind'].sel(time=time_str)
        except KeyError:
            raise Exception('Please make sure that time stamps of environmental data match full hours')

        twa, tws = self.get_twatws_from_uv(u,v)

        tws = tws.to_numpy()
        twa = twa.to_numpy()

        return {'twa': twa, 'tws': tws}

    def read_wind_functions(self, iTime):
        time = self.time_start + self.time_res*iTime
        #wind = self.nc_to_wind_function_old_format()
        wind = self.calculate_wind_function(time)

        if not (wind['twa'].shape==wind['tws'].shape): raise ValueError('Shape of twa and tws not matching!')

        lat_shape = wind['twa'].shape[0]
        lon_shape = wind['twa'].shape[1]
        #print('lat_shape', lat_shape)
        #print('long_shape', lon_shape)
        lats_grid = np.linspace(self.map_size.x1, self.map_size.x2, lat_shape)
        lons_grid = np.linspace(self.map_size.y1, self.map_size.y2, lon_shape)
        #print('lons shape', lons_grid.shape)

        f_twa = RegularGridInterpolator(
            (lats_grid, lons_grid), wind['twa'],
        )

        f_tws = RegularGridInterpolator(
            (lats_grid, lons_grid), wind['tws'],
        )

        return {'twa': f_twa, 'tws': f_tws, 'timestamp': time}

    def read_wind_vectors(self, time):
        """Return u-v components for given rect for visualization."""

        lat1 = self.map_size.x1
        lat2 = self.map_size.x2
        lon1 = self.map_size.y1
        lon2 = self.map_size.y2
        time_str = time.strftime('%Y-%m-%d %H:%M:%S')

        ds_time=self.ds.sel(time = time_str)

        u = ds_time['u-component_of_wind_maximum_wind'].where(
            (ds_time.latitude >= lat1) & (ds_time.latitude <= lat2) & (ds_time.longitude >= lon1) & (
                    ds_time.longitude <= lon2), drop=True)
        v = ds_time['v-component_of_wind_maximum_wind'].where(
            (ds_time.latitude >= lat1) & (ds_time.latitude <= lat2) & (ds_time.longitude >= lon1) & (
                    ds_time.longitude <= lon2), drop=True)
        lats_u_1D = ds_time['latitude'].where((ds_time.latitude >= lat1) & (ds_time.latitude <= lat2), drop=True)
        lons_u_1D = ds_time['longitude'].where((ds_time.longitude >= lon1) & (ds_time.longitude <= lon2), drop=True)

        u = u.to_numpy()
        v = v.to_numpy()
        lats_u_1D = lats_u_1D.to_numpy()
        lons_u_1D = lons_u_1D.to_numpy()
        lats_u = np.tile(lats_u_1D[:, np.newaxis], u.shape[1])
        lons_u = np.tile(lons_u_1D, (u.shape[0], 1))

        return {'u': u, 'v': v, 'lats_u': lats_u, 'lons_u': lons_u, 'timestamp': time}
