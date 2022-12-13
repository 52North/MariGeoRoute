import pytest
import numpy as np

from polars import Tanker

#def test_inc():
#    pol = Tanker(2)
#    assert pol.inc(3) == 5


def test_get_netCDF_courses():
    #lat = np.array([1., 1., 2, 2, 3, 3])
    #lon = np.array([4., 4., 3, 3, 5, 5])
    #courses = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
    #speed =  np.array([0.01, 0.02, 0.03, 0.04, 0.05, 0.06])

    lat = np.array([1., 1., 1, 2, 2, 2])
    lon = np.array([4., 4., 4, 3, 3, 3])
    courses = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
    speed =  np.array([0.01, 0.02, 0.03, 0.04, 0.05, 0.06])

    pol = Tanker (2)
    ds = pol.get_netCDF_courses(courses, lat, lon,  1)

    lat_read = ds['lat'].to_numpy()
    lon_read = ds['lon'].to_numpy()
    courses_read = ds['courses'].to_numpy()
    speed_read = ds['speed'].to_numpy()

    lat_ind = np.unique(lat, return_index=True)[1]
    lon_ind = np.unique(lon,return_index=True)[1]
    lat = [lat[index] for index in sorted(lat_ind)]
    lon = [lon[index] for index in sorted(lon_ind)]

    assert len(lat) == lat_read.shape[0]
    assert len(lon) == lon_read.shape[0]

    for i in range (0,lat_read.shape[0]):
        assert lat[i]==lat_read[i]
        assert lon[i]==lon_read[i]

    assert courses.shape[0] == courses_read.shape[0]*courses_read.shape[1]

    for ilat in range(0, courses_read.shape[0]):
        for iit in range(0, courses_read.shape[1]):
            iprev=ilat*courses_read.shape[1]+iit
            assert courses[iprev]==courses_read[ilat][iit]