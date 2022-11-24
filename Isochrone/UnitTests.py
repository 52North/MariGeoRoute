import numpy as np
import xarray as xr
import math
from weather import *


def test_twa_calculations():
    windfile = '/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/Data/2019122212/20205150000_split13.nc'
    model ='2020111600'
    start_time =start_time = dt.datetime.strptime('2020111600', '%Y%m%d%H')
    hours =10
    wt = WeatherCondCMEMS(windfile, model, start_time, hours, 3)
    u = 0.5
    v = 1
    twa, tws = wt.get_twatws_from_uv(u, v)
    #if not ((twa==225) and (tws == math.sqrt(2))) : raise ValueError('wrong calc')
    print('u=1, v=1')
    print('twa=', twa)
    print('tws=', tws)

    u = -0.5
    twa, tws = wt.get_twatws_from_uv(u, v)
    #if not ((twa == 135) and (tws == math.sqrt(2))): raise ValueError('wrong calc')
    print('u=1, v=1')
    print('twa=', twa)
    print('tws=', tws)

    v = -1
    twa, tws = wt.get_twatws_from_uv(u, v)
    #if not ((twa == 45) and (tws == math.sqrt(2))): raise ValueError('wrong calc')
    print('u=1, v=1')
    print('twa=', twa)
    print('tws=', tws)


def main():
    test_twa_calculations()

if __name__ == "__main__":
    main()