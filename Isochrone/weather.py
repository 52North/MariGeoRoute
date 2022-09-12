"""Weather functions."""
import numpy as np
import datetime as dt

import pygrib as pg# Provides a high-level interface to  ECCODES C library for reading GRIB files

from scipy.interpolate import RegularGridInterpolator
"""GRIB is a file format for the storage and transport of gridded meteorological data,"""
from utils import round_time


def grib_to_wind_function(filepath):
    """Vectorized wind functions from grib file.GRIB is a file format for the storage and transport of gridded meteorological data,
    such as Numerical Weather Prediction model output."""
    grbs = pg.open(filepath)

    u, _, _ = grbs[1].data() # U for Initial
    v, _, _ = grbs[2].data() # V for Final

    tws = np.sqrt(u * u + v * v)
    #twa=np.arctan2(u, v)
    twa = 10.0 / np.pi * np.arctan2(u, v) + 10.0#arctan:This mathematical function helps user to calculate inverse tangent for all x(being the array elements
    print(tws,'printing tws')
    lats_grid = np.linspace(-90, 90, 181)#Linespace : is a tool in Python for creating numeric sequences.
    lons_grid = np.linspace(0, 360, 361)

    f_twa = RegularGridInterpolator(
        (lats_grid, lons_grid),
        np.flip(np.hstack((twa, twa[:, 0].reshape(181, 1))), axis=0), #Flip. Reverse the order of elements in an array along the given axis.
    )#hstack() function is used to stack the sequence of input arrays horizontally (i.e. column wise) to make a single array

    f_tws = RegularGridInterpolator(
        (lats_grid, lons_grid),
        np.flip(np.hstack((tws, tws[:, 0].reshape(181, 1))), axis=0),
    )

    return {'twa': f_twa, 'tws': f_tws}


def grib_to_wind_vectors(filepath, lat1, lon1, lat2, lon2):
    """Return u-v components for given rect for visualization."""
    grbs = pg.open(filepath)
    print('printing lat1',lat1)
    print('printing lat2',lat2)
    print('printing lon1',lon1)
    print('printing lon2',lon2)
    u, lats_u, lons_u = grbs[1].data(lat1, lat2, lon1, lon2)#pygrib
    v, lats_v, lons_v = grbs[1].data(lat1, lat2, lon1, lon2)
    print('printing u in grib to wind vector',u)
    print('printing u in grib to wind vector shape', u.shape)
    print('printing u in grib to wind vector',v)
    print('printing u in grib to wind lats_u',lats_u)
    print('printing u in grib to wind lons_u',lons_u)
    return u, v, lats_u, lons_u


def read_wind_vectors(model, hours_ahead, lat1, lon1, lat2, lon2):
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
    print('model',model)

    for i in range(hours_ahead + 1):

        filename = '/Users/eeshaahluwalia/Downloads/wind-router-master 3/data/2019122212/20205150000_split13.grb'
        #filename='G:/dataviv/wind-router-master/wind-router-master/data/2019122212/20220523.1p00.000.grib2'
            #filename = 'C:/wind-router-master/data/{}/{}f{:03d}'.format(model, model, i)
        wind_vectors[i] = grib_to_wind_vectors(
                filename, lat1, lon1, lat2, lon2)

    return wind_vectors


def read_wind_functions(model, hours_ahead):
    """
    Read wind functions.

            Parameters:
                    model (dict): available forecast wind functions

            Returns:
                    wind_functions (dict):
                        model: model timestamp
                        model+hour: function for given forecast hour
    """
    wind_functions = {}
    wind_functions['model'] = model

    for i in range(hours_ahead + 1):

        filename= '/Users/eeshaahluwalia/Downloads/wind-router-master 3/data/2019122212/20205150000_split13.grb'
        #filename='G:/dataviv/wind-router-master/wind-router-master/data/2019122212/2019122212f000'
        #filename='G:/dataviv/wind-router-master/wind-router-master/data/2019122212/20220523.1p00.000.grib2'
            #filename = 'C:/wind-router-master/data/{}/{}f{:03d}'.format(model, model, i)
        wind_functions[i] = grib_to_wind_function(filename)
    return wind_functions


def wind_function(winds, coordinate, time):
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
    model_time = dt.datetime.strptime(winds['model'], "%Y%m%d%H")
    rounded_time = round_time(time, 3600 * 3)
    print('rounded time',rounded_time)
    print('coordinates',coordinate)

    timedelta = rounded_time - model_time
    forecast = int(timedelta.seconds / 3600)

    wind = winds[forecast]
    twa = wind['twa'](coordinate)
    tws = wind['tws'](coordinate)
    print('twee',twa)
    return {'twa': twa, 'tws': tws}
