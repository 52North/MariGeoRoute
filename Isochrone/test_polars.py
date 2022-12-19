import pytest
import numpy as np
import xarray as xr
import pandas as pd
import math

from polars import Tanker
import datetime

#def test_inc():
#    pol = Tanker(2)
#    assert pol.inc(3) == 5

def get_default_Tanker():
    DEFAULT_GFS_FILE = '/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/Data/20221110/38908a16-7a3c-11ed-b628-0242ac120003.nc'  # CMEMS needs lat: 30 to 45, lon: 0 to 20
    COURSES_FILE = '/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/CoursesRoute.nc'

    pol = Tanker(2)
    pol.init_hydro_model_Route(DEFAULT_GFS_FILE, COURSES_FILE)
    return pol

def compare_times(time64, time):
    time64 = (time64 - np.datetime64('1970-01-01T00:00:00Z'))/np.timedelta64(1, 's')
    time = (time - datetime.datetime(1970,1,1,0,0))
    for iTime in range(0,time.shape[0]): time[iTime] = time[iTime].total_seconds()
    assert np.array_equal(time64, time)
'''
    test whether lat, lon, time and courses are correctly written to course netCDF (elements and shape read from netCDF
     match properties of original array)
'''
def test_get_netCDF_courses():
    lat = np.array([1., 1., 1, 2, 2, 2])
    lon = np.array([4., 4., 4, 3, 3, 3])
    courses = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
    speed =  np.array([0.01, 0.02, 0.03, 0.04, 0.05, 0.06])

    pol = get_default_Tanker()
    time = np.array([datetime.datetime(2022, 12, 19), datetime.datetime(2022, 12, 19), datetime.datetime(2022, 12, 19),
                     datetime.datetime(2022, 12, 19)+datetime.timedelta(days=360), datetime.datetime(2022, 12, 19)+datetime.timedelta(days=360), datetime.datetime(2022, 12, 19)+datetime.timedelta(days=360)])

    pol.write_netCDF_courses(courses, lat, lon,  time)
    ds = xr.open_dataset(pol.courses_path)

    lat_read = ds['lat'].to_numpy()
    lon_read = ds['lon'].to_numpy()
    courses_read = ds['courses'].to_numpy()
    time_read = ds['time'].to_numpy()

    lat_ind = np.unique(lat, return_index=True)[1]
    lon_ind = np.unique(lon,return_index=True)[1]
    time_ind = np.unique(time,return_index=True)[1]
    lat = [lat[index] for index in sorted(lat_ind)]
    lon = [lon[index] for index in sorted(lon_ind)]
    time = [time[index] for index in sorted(time_ind)]
    time = np.array(time)

    assert np.array_equal(lat,lat_read)
    assert np.array_equal(lon,lon_read)
    compare_times(time_read,time)

    assert courses.shape[0] == courses_read.shape[0]*courses_read.shape[1]
    for ilat in range(0, courses_read.shape[0]):
        for iit in range(0, courses_read.shape[1]):
            iprev=ilat*courses_read.shape[1]+iit
            assert courses[iprev]==courses_read[ilat][iit]

'''
    test whether power is correctly extracted from courses netCDF
'''
def test_get_fuel_from_netCDF():
    lat = np.array([1.1,2.2,3.3,4.4])
    it = np.array([1, 2])
    power = np.array([[1,4], [3.4,5.3],
                          [2.1,6], [1.,5.1]])

    data_vars = dict(
        Power_delivered=(["lat", "it"], power),
    )

    coords = dict(
        lat=(["lat"], lat),
        it=(["it"], it),
    )
    attrs = dict(description="Necessary descriptions added here.")

    ds = xr.Dataset(data_vars, coords, attrs)
    print(ds)

    pol = get_default_Tanker()
    power_test = pol.extract_fuel_from_netCDF(ds)
    power_ref = np.array([1,4, 3.4,5.3, 2.1,6, 1.,5.1])

    print('power_test', power_test)

    for i in range(0,power_ref.shape[0]):
        assert power_ref[i] == power_test[i]
'''
    test whether all variablies and dimensions that are passed in courses netCDF to mariPower are returned back correctly
'''
def test_get_fuel_netCDF_return_values():
    lat = np.array([1.1, 2.2, 3.3, 4.4])
    it = np.array([1, 2])
    time = np.array([datetime.datetime(2022, 12, 19),datetime.datetime(2022, 12, 19),datetime.datetime(2022, 12, 19),datetime.datetime(2022, 12, 19)])

    lon = np.array([0.1,0.2,0.3,0.4])
    speed = np.array([[5,5],[5,5],
                      [5,5],[5,5]])
    courses = np.array([[10,11],[12,14],
                       [14,16],[15,16]])

    power = np.array([[1, 4], [3.4, 5.3],
                      [2.1, 6], [1., 5.1]])

    data_vars = dict(
        lon = (["lat"], lon),
        time = (["time"], time),
        speed=(["lat", "it"], speed),
        courses=(["lat", "it"], courses),
    )

    coords = dict(
        lat=(["lat"], lat),
        it=(["it"], it),
    )
    attrs = dict(description="Necessary descriptions added here.")

    ds = xr.Dataset(data_vars, coords, attrs)

    pol = get_default_Tanker()

    ds.to_netcdf(pol.courses_path)
    ds_read = pol.get_fuel_netCDF()

    lon_test = ds_read['lon'].to_numpy()
    lat_test = ds_read['lat'].to_numpy()
    speed_test = ds_read['speed'].to_numpy()
    courses_test = ds_read['courses'].to_numpy()
    it_test = ds_read['it'].to_numpy()

    assert np.array_equal(lon_test, lon)
    assert np.array_equal(lat_test, lat)
    assert np.array_equal(speed_test, speed)
    assert np.array_equal(courses_test, courses)
    assert np.array_equal(it_test, it)

'''
    test whether single netCDFs which contain information for one course per pixel are correctly merged
'''
def test_get_fuel_netCDF_loop():
    lat = np.array([1.1, 2.2, 3.3, 4.4])
    it = np.array([1, 2])
    time = np.array([datetime.datetime(2022, 12, 19), datetime.datetime(2022, 12, 19), datetime.datetime(2022, 12, 19),
                     datetime.datetime(2022, 12, 19)])

    lon = np.array([0.1, 0.2, 0.3, 0.4])
    speed = np.array([[5, 5], [5, 5],
                      [5, 5], [5, 5]])
    courses = np.array([[10, 11],
                        [12, 14],
                        [14, 16],
                        [15, 16]])

    power = np.array([[1, 4], [3.4, 5.3],
                      [2.1, 6], [1., 5.1]])

    data_vars = dict(
        lon=(["lat"], lon),
        time=(["lat"], time),
        speed=(["lat", "it"], speed),
        courses=(["lat", "it"], courses),
    )

    coords = dict(
        lat=(["lat"], lat),
        it=(["it"], it),
    )
    attrs = dict(description="Necessary descriptions added here.")

    ds = xr.Dataset(data_vars, coords, attrs)

    pol = get_default_Tanker()

    ds.to_netcdf(pol.courses_path)
    ds_read = pol.get_fuel_netCDF_loop()

    lon_test = ds_read['lon'].to_numpy()
    lat_test = ds_read['lat'].to_numpy()
    speed_test = ds_read['speed'].to_numpy()
    courses_test = ds_read['courses'].to_numpy()
    it_test = ds_read['it'].to_numpy()
    time_test = ds_read['time'].to_numpy()
    power_test = ds_read['Power_delivered'].to_numpy()

    assert np.array_equal(lat_test, lat)
    assert np.array_equal(it_test, it)
    assert np.array_equal(courses_test, courses)
    assert np.array_equal(lon_test, lon)
    assert np.array_equal(speed_test, speed)

    compare_times(time_test, time)
    assert power_test.shape == courses_test.shape
    assert (power_test < math.pow(10,30)).all


