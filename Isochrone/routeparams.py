import numpy as np
import datetime as dt
from typing import NamedTuple


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
    full_dist_travelled: np.ndarray  # full geodesic distance since start

    def __init__(self, count, start, finish, fuel, rpm, route_type, time, lats_per_step, lons_per_step, azimuths_per_step, dists_per_step, full_dist_travelled):
        self.count = count,  # routing step
        self.start = start,  # lat, lon at start
        self.finish = finish,  # lat, lon at end
        self.fuel = -999,  # sum of fuel consumption [t]
        self.rpm = -999,  # propeller [revolutions per minute]
        self.route_type = route_type,  # route name
        self.time = time,  # time needed for the route [seconds]
        self.lats_per_step = lats_per_step
        self.lons_per_step = lons_per_step
        self.azimuths_per_step = azimuths_per_step
        self.dists_per_step = dists_per_step
        self.full_dist_travelled = full_dist_travelled

    def print_route(self):
        print('Printing route from ' + str(self.route_type))
        print(self.start)
        print('to')
        print(self.finish)
        print('routing steps ' + str(self.count))
        print('time needed ' + str(self.time))
        print('fuel needed' + str(self.fuel))
        print('rpm needed' + str(self.rpm))
        print('lats_per_step ' + str(self.lats_per_step))
        print('lons_per_step ' + str(self.lons_per_step))
        print('azimuths_per_step ' + str(self.azimuths_per_step))
        print('dists_per_step ' + str(self.dists_per_step))
        print('full_dist_travelled ' + str(self.full_dist_travelled))
