import numpy as np
import datetime as dt
from geovectorslib import geod
from global_land_mask import globe

from routeparams import RouteParams
from IsoBased import IsoBased
import utils

class RoutingAlgTimeMin(IsoBased):
    delta_time : int

    def __init__(self, start, finish, time, delta_time):
        IsoBased.__init__(self, start, finish, time)
        self.delta_time = delta_time

    def get_current_azimuth(self):
        return self.current_variant

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

    def get_dist(self, bs):
        dist = self.delta_time * bs
        print('dist=', dist)
        print('delta_time=', self.delta_time)
        print('bs=', bs)
        return dist

    def get_delta_variables(self, boat, wind, bs):
        dist = self.get_dist(bs)
        delta_fuel = boat.get_fuel_per_time(self.get_current_azimuth(), wind) * self.delta_time

        return self.delta_time, delta_fuel, dist
