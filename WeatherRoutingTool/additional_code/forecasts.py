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
"""Module to download GFS model grib2 files."""
""" The Global Forecast System (GFS) is a National Centers for Environmental Prediction (NCEP) weather 
forecast model that generates data for dozens of atmospheric and land-soil
 variables, including temperatures, winds, precipitation, soil moisture, and atmospheric ozone concentration"""
"""GRIB is a file format for the storage and transport of gridded meteorological data, 
such as Numerical Weather Prediction model output . """
import os

from lxml import etree

import requests


def get_latest_gfs_timestamp(model='1p00'):
    """Find the latest current gfs and forecasts and download the file."""
    url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_{}.pl'.format(model)
    html = etree.HTML(requests.get(url).content)
    dates = html.xpath('//tr//td/a/text()')
    latest_date = dates[0]

    # latest hour
    url = url + '?dir=%2F{}'.format(latest_date)
    html = etree.HTML(requests.get(url).content)
    hours = html.xpath('//tr//td/a/text()')
    latest_hour = hours[0]

    # check if latest exists and if not - roll back by 6hrs
    url = url + '%2F{}'.format(latest_hour)
    html = etree.HTML(requests.get(url).content)
    e = html.xpath('.//font[contains(text(),"No files or directories found")]')
    if len(e) != 0:
        if latest_hour == '00':
            latest_date = 'gfs.{}'.format(str(int(latest_date[4:]) - 1))
            latest_hour = '18'
        else:
            latest_hour = '{:02d}'.format(int(latest_hour) - 6)

    # trim gfs
    latest_date = latest_date[4:]

    return latest_date, latest_hour


def download_gfs_for_timestamp(date, hour, fcst, model='1p00'):
    """
    Download GFS grib files with forecast for specific date and hour.

    Sources:
    https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25_1hr.pl?file=gfs.t18z.pgrb2.0p25.anl&lev_0.995_sigma_level=on&var_UGRD=on&var_VGRD=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgfs.20201109%2F18
    https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25_1hr.pl?file=gfs.t18z.pgrb2.0p25.f000&lev_0.995_sigma_level=on&var_UGRD=on&var_VGRD=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgfs.20201109%2F18
    """
    url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_{}.pl'.format(model)
    fileurl = '?file=gfs.t{}z.pgrb2.{}.f{:03d}'.format(hour, model, fcst)
    filter = '&lev_10_m_above_ground=on&var_UGRD=on&var_VGRD=on&leftlon=0&' +\
             'rightlon=360&toplat=90&bottomlat=-90'
    dir = '&dir=%2Fgfs.{}%2F{}'.format(date, hour)
    url = url + fileurl + filter + dir

    folder = '{}{}'.format(date, hour)
    filename = folder + 'f{:03d}'.format(fcst)

    # create folder
    try:
        os.mkdir(os.path.join("/data", folder))
    except:
        pass

    # write file
    try:
        r = requests.get(url)
        path = os.path.join("/data", folder, filename)

        with open(path, 'wb') as f:
            f.write(r.content)
    except:
        pass
    return path


def download_gfs_forecasts(date, hour, fcst_to_download):
    """Donwload gfs with a given number of forecast files."""
    for i in range(fcst_to_download):
        fcst = i * 3
        path = download_gfs_for_timestamp(date, hour, fcst)
    return path

if __name__ == '__main__':
    date = '20201116'
    hour = '00'
    fcst_to_download = 41
    download_gfs_forecasts(date, hour, fcst_to_download)
