import numpy as np
import datetime as dt
from geovectorslib import geod
from global_land_mask import globe

from routeparams import RouteParams
from IsoBased import IsoBased
import utils

class IsoFuel(IsoBased):
    delta_fuel : float

    def __init__(self, start, finish, time, delta_fuel):
        IsoBased.__init__(self, start, finish, time)
        self.delta_fuel = delta_fuel

    def check_isochrones(self, route : RouteParams):
        print('To be implemented')

    def get_dist(self, bs, delta_time):
        dist = delta_time * bs
        return dist

    def get_delta_variables(self, boat, wind, bs):
        fuel = boat.get_fuel_per_time(self.get_current_azimuth(), wind)
        delta_time = self.delta_fuel/fuel*3600
        dist = self.get_dist(bs, delta_time)

        #print('delta_fuel=' + str(fuel) + ' , delta_time=' + str(delta_time) + ' , dist=' + str(dist))
        delta_fuel = np.repeat(self.delta_fuel, wind['twa'].shape)

        return delta_time, delta_fuel, dist

    def get_delta_variables_netCDF(self, boat, wind, bs):
        #fuel = boat.get_fuel_per_time_netCDF(self.get_current_azimuth(), self.get_current_lats(),
        #                                           self.get_current_lons(), self.time)
        fuel = boat.get_fuel_per_time(self.get_current_azimuth(), wind)
        delta_time = self.delta_fuel / fuel * 3600
        dist = self.get_dist(bs, delta_time)

        # print('delta_fuel=' + str(fuel) + ' , delta_time=' + str(delta_time) + ' , dist=' + str(dist))
        delta_fuel = np.repeat(self.delta_fuel, bs.shape)

        self.determine_timespread(self,delta_time)

        return delta_time, delta_fuel, dist

    def determine_timespread(self, delta_time):
        stddev = np.std(delta_time)
        mean = np.mean(delta_time)
        print('spread of time: ' + str(mean) + '+-' + str(stddev))

    def update_time(self, delta_time):
        if not ((self.full_time_traveled.shape == delta_time.shape) and (self.time.shape == delta_time.shape)): raise ValueError('shapes of delta_time, time and full_time_traveled not matching!')
        for i in range(0,self.full_time_traveled.shape[0]):
            self.full_time_traveled[i] += delta_time[i]
            self.time[i] += dt.timedelta(seconds=delta_time[i])

