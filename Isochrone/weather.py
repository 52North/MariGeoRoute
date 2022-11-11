"""Weather functions."""
import numpy as np
import datetime as dt
import xarray as xr
import bbox as bbox
from bbox import BBox2D, XYXY

import pygrib as pg

from scipy.interpolate import RegularGridInterpolator

from utils import round_time


class WeatherCond():
    model: str
    time_steps: int
    time_res: dt.timedelta
    time_start: dt.datetime
    map_size: bbox.BBox2D
    ds: xr.Dataset
    wind_functions: None

    def __init__(self, filepath, model, time, hours, time_res):
        self.model = model
        self.time_steps = hours
        self.time_res = time_res
        self.time_start = time

        self.read_dataset(filepath)

    @property
    def time_res(self):
        return self._time_res

    @time_res.setter
    def time_res(self, value):
        if (value < 3): raise ValueError('Resolution below 3h not possible')
        self._time_res = dt.timedelta(hours=value)
        print('Setting time resolution to ' + str(self.time_res) + ' hours')


    def set_map_size(self, lat1, lon1, lat2, lon2):
        self.map_size=BBox2D([lat1, lon1, lat2, lon2], mode=XYXY)


    def read_dataset(self, filepath):
        print('Reading dataset from', filepath)
        self.ds = xr.open_dataset(filepath)
        # print('dataset', self.ds)

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

    def nc_to_wind_vectors(self, lat1, lon1, lat2, lon2):
        """Return u-v components for given rect for visualization."""

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

        return u, v, lats_u, lons_u

    '''
    def grib_to_wind_vectors(filepath, lat1, lon1, lat2, lon2):
        """Return u-v components for given rect for visualization."""
        grbs = pg.open(filepath)
        u, lats_u, lons_u = grbs[1].data(lat1, lat2, lon1, lon2)
        v, lats_v, lons_v = grbs[2].data(lat1, lat2, lon1, lon2)
        return u, v, lats_u, lons_u
    '''

    def read_wind_vectors(self, model, hours_ahead, lat1, lon1, lat2, lon2):
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
        wind_vectors['model'] = model

        for i in range(hours_ahead + 1):
            wind_vectors[i] = self.nc_to_wind_vectors(lat1, lon1, lat2, lon2)

        return wind_vectors

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

        for i in range(self.time_steps + 1):
            wind_function[i] = self.get_wind_function(i)

        self.wind_functions = wind_function

    def wind_function(self, coordinate, time):
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
        rounded_time = round_time(time, int(self.time_res.total_seconds()))
        time_passed = rounded_time-self.time_start
        time_steps_passed = (time_passed.total_seconds()/self.time_res.total_seconds())
        if not (rounded_time==self.wind_functions[time_steps_passed]['timestamp']):
            ex = 'Accessing wrong weather forecast. Accessing element ' + str(self.wind_functions[time_steps_passed]['timestamp']) + ' but current rounded time is ' + str(rounded_time)
            raise Exception(ex)

        wind = self.wind_functions[time_steps_passed]
        twa = wind['twa'](coordinate)
        tws = wind['tws'](coordinate)

        return {'twa': twa, 'tws': tws}

class WeatherCondNCEP(WeatherCond):
    def __init__(self, filepath, model, time, hours, time_res):
        WeatherCond.__init__(self, filepath, model, time, hours, time_res)
        print('WARNING: not well maintained. Currently one data file for one particular times is read several times')
        
    def nc_to_wind_function(self):
        """Vectorized wind functions from NetCDF file."""

        tws = np.sqrt(self.ds.u10 ** 2 + self.ds.v10 ** 2)
        twa = 180.0 / np.pi * np.arctan2(self.ds.u10, self.ds.v10) + 180.0

        tws = tws.to_numpy()
        twa = twa.to_numpy()

        return {'twa': twa, 'tws': tws}

    def get_wind_function(self, iTime):
        time = self.time_start + self.time_res*iTime

        wind = self.nc_to_wind_function()

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

class WeatherCondCMEMS(WeatherCond):
    def nc_to_wind_function(self, time):
        time_str=time.strftime('%Y-%m-%d %H:%M:%S')
        print('Reading time', time_str)

        u = self.ds['u-component_of_wind_maximum_wind'].sel(time=time_str)
        v = self.ds['v-component_of_wind_maximum_wind'].sel(time=time_str)

        tws = np.sqrt(u ** 2 + v ** 2)
        twa = 180.0 / np.pi * np.arctan2(u, v) + 180.0

        tws = tws.to_numpy()
        twa = twa.to_numpy()

        return {'twa': twa, 'tws': tws}

    def get_wind_function(self, iTime):
        time = self.time_start + self.time_res*iTime
        #wind = self.nc_to_wind_function_old_format()
        wind = self.nc_to_wind_function(time)

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