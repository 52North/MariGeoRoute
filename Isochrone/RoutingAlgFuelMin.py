import numpy as np
import datetime as dt
from geovectorslib import geod
from global_land_mask import globe

from routeparams import RouteParams
from IsoBased import IsoBased
import utils

class RoutingAlgFuelMin(IsoBased):
    delta_fuel : float

    def __init__(self, start, finish, time):
        IsoBased.__init__(self, start, finish, time)

    def define_initial_variants(self):
        self.full_time_traveled = np.repeat(0., self.variant_segments + 1, axis=0)

    def get_current_azimuth(self):
        return self.current_variant

    def update_time(self, delta_time):
        self.full_time_traveled += delta_time
        self.time += dt.timedelta(seconds=delta_time)

    def update_fuel(self, delta_fuel):
        self.full_fuel_consumed += delta_fuel

    def crosses_land(self):
        debug = False

        LandCrossingSteps = 10
        delta_lats = (self.lats_per_step[0, :] - self.lats_per_step[1, :]) / LandCrossingSteps
        delta_lons = (self.lons_per_step[0, :] - self.lons_per_step[1, :]) / LandCrossingSteps
        x0 = self.lats_per_step[1, :]
        y0 = self.lons_per_step[1, :]
        print('lats_per_step shape',  self.lats_per_step.shape[1] )
        is_on_land = [False for i in range(0, self.lats_per_step.shape[1])]

        if(debug):
            print('Moving from (' + str(self.lats_per_step[1, :]) + ',' + str(self.lons_per_step[1, :]) + ') to (' + str(self.lats_per_step[0, :]) + ',' + str(self.lons_per_step[0, :]))
            print('x0=' + str(x0) + ', y0=' + str(y0))
            print('is_on_land', is_on_land)
            print('delta_lats', delta_lats)
            print('delta_lons', delta_lons)

        for iStep in range(0, LandCrossingSteps):
            x = x0 + delta_lats
            y = y0 + delta_lons
            if (debug):
                print('     iStep=', iStep)
                print('     x=', x)
                print('     y=', y)

            is_on_land_temp = globe.is_land(x,y)
            print('is_on_land_temp', is_on_land_temp)
            is_on_land = is_on_land + is_on_land_temp
            print('is_on_land', is_on_land)
            x0 = x
            y0 = y


        #if not ((round(x0.all,8) == round(self.lats_per_step[0, :].all) and (x0.all == self.lons_per_step[0, :].all)):
        #    exc = 'Did not check destination, only checked lat=' + str(x0) + ', lon=' + str(y0)
        #    raise ValueError(exc)

        return is_on_land

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
        print('To be implemented')