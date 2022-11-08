import numpy as np
import datetime as dt
from typing import NamedTuple

import utils


class RouteParams():
    """
        Isochrone data structure with typing.
                Parameters:
                    count: int  (routing step)
                    start: tuple    (lat,long at start)
                    finish: tuple   (lat,lon and end)
                    gcr_azi: float (initial gcr heading)
                    lats1, lons1, azi1, s12: (M, N) arrays, N=headings+1, M=number of steps+1 (decreasing step number)
                    azi0, s0: (M, 1) vectors without history
                    time1: current datetime
                    elapsed: complete elapsed timedelta
        """
    count: int  # routing step
    start: tuple  # lat, lon at start
    finish: tuple  # lat, lon at end
    fuel: float  # sum of fuel consumption [t]
    rpm: int  # propeller [revolutions per minute]
    route_type: str  # route name
    time: dt.timedelta  # time needed for the route [seconds]
    lats_per_step: np.ndarray  # lats: (M,N) array, N=headings+1, M=steps (M decreasing)
    lons_per_step: np.ndarray  # longs: (M,N) array, N=headings+1, M=steps
    azimuths_per_step: np.ndarray  # azimuth: (M,N) array, N=headings+1, M=steps [degree]
    dists_per_step: np.ndarray  # geodesic distance traveled per time stamp: (M,N) array, N=headings+1, M=steps
    full_dist_traveled: np.ndarray  # full geodesic distance since start

    def __init__(self, count, start, finish, fuel, rpm, route_type, time, lats_per_step, lons_per_step, azimuths_per_step, dists_per_step, full_dist_traveled):
        self.count = count  # routing step
        self.start = start  # lat, lon at start
        self.finish = finish  # lat, lon at end
        self.fuel = fuel  # sum of fuel consumption [t]
        self.rpm = rpm  # propeller [revolutions per minute]
        self.route_type = route_type  # route name
        self.time = time  # time needed for the route [seconds]
        self.lats_per_step = lats_per_step
        self.lons_per_step = lons_per_step
        self.azimuths_per_step = azimuths_per_step
        self.dists_per_step = dists_per_step
        self.full_dist_traveled = full_dist_traveled

    def print_route(self):
        utils.print_line()
        print('Printing route:  ' + str(self.route_type))
        print('Going from', self.start)
        print('to')
        print(self.finish)
        print('routing steps ' + str(self.count))
        print('time ' + str(self.time))
        print('fuel ' + str(self.fuel))
        print('rpm ' + str(self.rpm))
        print('lats_per_step ' + str(self.lats_per_step))
        print('lons_per_step ' + str(self.lons_per_step))
        print('azimuths_per_step ' + str(self.azimuths_per_step))
        print('dists_per_step ' + str(self.dists_per_step))
        print('full_dist_traveled ' + str(self.full_dist_traveled))
        utils.print_line()

    def __eq__(self, route2):
        bool_equal=True
        if not (self.count == route2.count):
            raise ValueError('Route counts not matching')
        if not (np.array_equal(self.start, route2.start)):
            raise ValueError('Route start not matching')
        if not (np.array_equal(self.finish, route2.finish)):
            raise ValueError('Route finsh not matching')
        if not (np.array_equal(self.time, route2.time)):
            raise ValueError('Route time not matching: self=' + str(self.time) + ' other=' + str(route2.time))
        if not (np.array_equal(self.fuel, route2.fuel)):
            raise ValueError('Route fuel not matching: self=' + str(self.fuel) + ' other=' + str(route2.fuel))
        if not (np.array_equal(self.rpm, route2.rpm)):
            raise ValueError('Route rpm not matching')
        if not (np.array_equal(self.lats_per_step, route2.lats_per_step)):
            raise ValueError('Route lats_per_step not matching')
        if not (np.array_equal(self.lons_per_step, route2.lons_per_step)):
            raise ValueError('Route lons_per_step not matching')
        if not (np.array_equal(self.azimuths_per_step, route2.azimuths_per_step)):
            raise ValueError('Route azimuths_per_step not matching')
        if not (np.array_equal(self.dists_per_step, route2.dists_per_step)):
            raise ValueError('Route dists_per_step not matching')
        if not (np.array_equal(self.full_dist_traveled, route2.full_dist_traveled)):
            raise ValueError('Route full_dist_traveled not matching')

        return bool_equal