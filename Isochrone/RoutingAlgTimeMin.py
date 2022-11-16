import numpy as np
import datetime as dt
import utils as ut
from polars import Boat
from typing import NamedTuple
from geovectorslib import geod
from weather import WeatherCond
from global_land_mask import globe
from scipy.stats import binned_statistic
from routeparams import RouteParams
from RoutingAlg import RoutingAlg
from IsoBased import IsoBased
import utils

class RoutingAlgTimeMin(IsoBased):
    def __init__(self, start, finish, time):
        IsoBased.__init__(self, start, finish, time)

    def define_initial_variants(self):
        self.full_time_traveled = np.repeat(0., self.variant_segments + 1, axis=0)

    def get_current_azimuth(self):
        return self.current_variant

    def update_time(self, delta_time, bs):
        self.full_time_traveled += delta_time
        self.time += dt.timedelta(seconds=delta_time)

    def update_dist(self, delta_time,bs, current_lats, current_lons):
        debug = False

        dist = delta_time * bs
        move = geod.direct(current_lats, current_lons, self.current_variant, dist)    #calculate new isochrone, update position and distance traveled
        self.lats_per_step = np.vstack((move['lat2'], self.lats_per_step))
        self.lons_per_step = np.vstack((move['lon2'], self.lons_per_step))
        self.dist_per_step = np.vstack((dist, self.dist_per_step))
        self.azimuth_per_step = np.vstack((self.current_variant, self.azimuth_per_step))

        if (debug):
            print('path of this step' +
                 # str(move['lat1']) +
                 # str(move['lon1']) +
                  str(move['lat2']) +
                  str(move['lon2']))
            print('dist', dist)
            print('bs=', self.speed_per_step)

        start_lats = np.repeat(self.start[0], self.lats_per_step.shape[1])
        start_lons = np.repeat(self.start[1], self.lons_per_step.shape[1])
        gcrs = geod.inverse(start_lats, start_lons, move['lat2'], move['lon2'])       #calculate full distance traveled, azimuth of gcr connecting start and new position
        self.current_variant = gcrs['azi1']
        self.current_azimuth = gcrs['azi1']

        # remove those which ended on land
        is_on_land = globe.is_land(move['lat2'], move['lon2'])
        #print('is_on_land', is_on_land)
        gcrs['s12'][is_on_land] = 0
        #crosses_land = self.crosses_land()
        #gcrs['s12'][crosses_land] = 0
        self.full_dist_traveled = gcrs['s12']






        # for i in range(int((x2 - x1) / STEP) + 1): #62.3, 17.6, 59.5, 24.6
        #     try:
        #         x = x1 + i * STEP
        #         y = (y1 - y2) / (x1 - x2) * (x - x1) + y1
        #     except:
        #         continue
        #     is_on_land = globe.is_land(float(x), float(y))
        #     print(is_on_land)
        #     # if not is_on_land:
        #     # print("in water")
        #
        #     if is_on_land:
        #         # print("crosses land")
        #
        #         return True

        # print('isonland',is_on_land)
        # z = globe.is_land(lats, lons)
        # print('value of z',type(z))
        # if z=='True':
        #     is_on_land = globe.is_land(move['lats2'], move['lons2'])
        #     print(is_on_land)

        # print(self)


    def get_wind_functions(self, wt):
        debug = False
        winds = wt.get_wind_function((self.current_lats, self.current_lons), self.time[0])
        if(debug):
            print('obtaining wind function for position: ', self.current_lats, self.current_lons)
            print('time', self.time[0])
            print('winds', winds)
        return winds

    def check_isochrones(self, route : RouteParams):
        debug=False
        if(debug) : print('Checking route for equal time intervals')

        route.print_route()
        for step in range(1,route.count):
            lat1=np.array([float(route.lats_per_step[step-1])])
            lat2=np.array([float(route.lats_per_step[step])])
            lon1=np.array([float(route.lons_per_step[step-1])])
            lon2=np.array([float(route.lons_per_step[step])])
            dist = geod.inverse(lat1, lon1, lat2, lon2)
            time = round(dist['s12'][0]/route.speed_per_step[step])

            if(debug):
                print('Step', step)
                print('lat1 ' + str(lat1) + ' lat2=' + str(lon1) + ' lat2=' + str(lat2) + 'lon2=' + str(lon2))
                print('speed=', route.speed_per_step[step])
                print('dist=', dist['s12'])
                print('time for step ' + str(step) + ' = ' + str(time))

            if not (time==3600):
                exc = 'Timestep ' + str(step) + ' of min.-time route are not equal to ' + str(3600) + ' but ' + str(time)
                raise ValueError(exc)
