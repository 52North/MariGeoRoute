import numpy as np
import datetime as dt
from typing import NamedTuple


class Isochrone(NamedTuple):
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
    gcr_azi: float          #initial azimuth
    lats1: np.ndarray       #lats: (M,N) array, N=headings+1, M=steps (M decreasing)
    lons1: np.ndarray       #longs: (M,N) array, N=headings+1, M=steps
    azi12: np.ndarray       #azimuth: (M,N) array, N=headings+1, M=steps
    s12: np.ndarray         #geodesic distance traveled per time stamp: (M,N) array, N=headings+1, M=steps
    azi02: np.ndarray       #current azimuth
    s02: np.ndarray         #full geodesic distance since start
    time1: dt.datetime      #current datetime
    elapsed: dt.timedelta   #time elapsed since start


