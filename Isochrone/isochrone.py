import numpy as np
import datetime as dt
from typing import NamedTuple


class Isochrone(NamedTuple):
    count: int                  
    start: tuple                
    finish: tuple               
    gcr_azi: float              
    lats1: np.ndarray           
    lons1: np.ndarray           
    azi12: np.ndarray           
    s12: np.ndarray             
    azi02: np.ndarray         
    s02: np.ndarray             
    time1: dt.datetime
    elapsed: dt.timedelta


