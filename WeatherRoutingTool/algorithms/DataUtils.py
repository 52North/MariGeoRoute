#   Copyright (C) 2021 - 2023 52°North Spatial Information Research GmbH
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# If the program is linked with libraries which are licensed under one of
# the following licenses, the combination of the program with the linked
# library is not considered a "derivative work" of the program:
#
#     - Apache License, version 2.0
#     - Apache Software License, version 1.0
#     - GNU Lesser General Public License, version 3
#     - Mozilla Public License, versions 1.0, 1.1 and 2.0
#     - Common Development and Distribution License (CDDL), version 1.0
#
# Therefore the distribution of the program linked with libraries licensed
# under the aforementioned licenses, is permitted by the copyright holders
# if the distribution is compliant with both the GNU General Public
# License version 2 and the aforementioned licenses.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
from skimage.graph import route_through_array
import xarray as xr
import numpy as np
from matplotlib import pyplot as plt
import os


def loadData(path):
    '''
    This function take a string as the path of the file and load the data from the file.
    Parameters:
    path: String, path of the file
    Returns:
    data: xarray, dataset
    '''
    # Path of the data file
    file = os.path.join(path,'mfwamglocep_2020120200_R20201203.nc')

    # read the dataset
    data = xr.open_dataset(file)
    data = data.VHM0.isel(time=0)
    return data

# create a bounding box from the coordinates
# NY to Lisbon 
def get_closest(array, value):
    return np.abs(array - value).argmin()

def getBBox(lon1, lat1,lon2,lat2, data):
    bbox = ((lon1, lat1),(lon2, lat2))
    time_slice = 0
    lon_min = get_closest(data.longitude.data, bbox[0][0])
    lat_min = get_closest(data.latitude.data, bbox[0][1])
    lon_max = get_closest(data.longitude.data, bbox[1][0])
    lat_max = get_closest(data.latitude.data, bbox[1][1])
    return lon_min, lon_max, lat_min, lat_max

def cleanData(data):
    # copy the data and remove NaN
    #cost = wave_height.data
    cost = data.copy()
    #np.random.shuffle(cost)
    nan_mask = np.isnan(cost)
    cost[nan_mask] = 2* np.nanmax(cost) if np.nanmax(cost) else 0

    return cost

def findStartAndEnd(lat1, lon1, lat2, lon2, wave_height):
    # Define start and end points
    lat_NY = lat1
    lon_NY = lon1
    lat_LS = lat2
    lon_LS = lon2

    start_lon = get_closest(wave_height.longitude.data, lon_NY)
    start_lat = get_closest(wave_height.latitude.data, lat_NY)
    end_lon = get_closest(wave_height.longitude.data,lon_LS)
    end_lat = get_closest(wave_height.latitude.data,lat_LS)

    start = (start_lat, start_lon)
    end = (end_lat, end_lon)

    return start, end
