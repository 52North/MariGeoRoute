import numpy as np
import datetime as dt
from typing import NamedTuple


class RouteParams(NamedTuple):
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
    count: int              #routing step
    start: tuple            #lat, lon at start
    finish: tuple           #lat, lon at end
    fuel: float             #sum of fuel consumption [t]
    rpm: int                #propeller [revolutions per minute]
    route_type: str         #route name
    time: dt.timedelta      #time needed for the route [seconds]
    lats_per_step: np.ndarray       #lats: (M,N) array, N=headings+1, M=steps (M decreasing)
    lons_per_step: np.ndarray       #longs: (M,N) array, N=headings+1, M=steps
    azimuths_per_step: np.ndarray       #azimuth: (M,N) array, N=headings+1, M=steps [degree]
    dists_per_step: np.ndarray         #geodesic distance traveled per time stamp: (M,N) array, N=headings+1, M=steps
    full_dist_travelled: np.ndarray         #full geodesic distance since start

