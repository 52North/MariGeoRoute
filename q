919d95cb Isochrone/isochrone.py  (Katharina Demmich 2022-10-24 16:17:37 +0200   1) import numpy as np
919d95cb Isochrone/isochrone.py  (Katharina Demmich 2022-10-24 16:17:37 +0200   2) import datetime as dt
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100   3) import utils as ut
b367a683 Isochrone/RoutingAlg.py (Katharina Demmich 2022-12-16 11:45:23 +0100   4) import time
b367a683 Isochrone/RoutingAlg.py (Katharina Demmich 2022-12-16 11:45:23 +0100   5) 
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100   6) from polars import Boat
919d95cb Isochrone/isochrone.py  (Katharina Demmich 2022-10-24 16:17:37 +0200   7) from typing import NamedTuple
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100   8) from geovectorslib import geod
b66d80b8 Isochrone/isochrone.py  (Katharina Demmich 2022-11-11 08:50:36 +0100   9) from weather import WeatherCond
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100  10) from global_land_mask import globe
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100  11) from scipy.stats import binned_statistic
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100  12) from routeparams import RouteParams
2690bf87 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-27 11:13:24 +0100  13) import matplotlib
d44e737a Isochrone/isochrone.py  (Katharina Demmich 2022-11-14 15:53:33 +0100  14) from matplotlib.figure import Figure
2690bf87 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-27 11:13:24 +0100  15) from matplotlib.axes import Axes
d44e737a Isochrone/isochrone.py  (Katharina Demmich 2022-11-14 15:53:33 +0100  16) import graphics
d8ab9da6 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-26 12:48:24 +0100  17) import logging
d44e737a Isochrone/isochrone.py  (Katharina Demmich 2022-11-14 15:53:33 +0100  18) 
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100  19) import utils
b367a683 Isochrone/RoutingAlg.py (Katharina Demmich 2022-12-16 11:45:23 +0100  20) from Constraints import *
919d95cb Isochrone/isochrone.py  (Katharina Demmich 2022-10-24 16:17:37 +0200  21) 
d8ab9da6 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-26 12:48:24 +0100  22) logger = logging.getLogger('WRT.routingalg')
919d95cb Isochrone/isochrone.py  (Katharina Demmich 2022-10-24 16:17:37 +0200  23) 
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100  24) class RoutingAlg():
919d95cb Isochrone/isochrone.py  (Katharina Demmich 2022-10-24 16:17:37 +0200  25)     """
919d95cb Isochrone/isochrone.py  (Katharina Demmich 2022-10-24 16:17:37 +0200  26)         Isochrone data structure with typing.
919d95cb Isochrone/isochrone.py  (Katharina Demmich 2022-10-24 16:17:37 +0200  27)                 Parameters:
919d95cb Isochrone/isochrone.py  (Katharina Demmich 2022-10-24 16:17:37 +0200  28)                     count: int  (routing step)
919d95cb Isochrone/isochrone.py  (Katharina Demmich 2022-10-24 16:17:37 +0200  29)                     start: tuple    (lat,long at start)
919d95cb Isochrone/isochrone.py  (Katharina Demmich 2022-10-24 16:17:37 +0200  30)                     finish: tuple   (lat,lon and end)
919d95cb Isochrone/isochrone.py  (Katharina Demmich 2022-10-24 16:17:37 +0200  31)                     gcr_azi: float (initial gcr heading)
919d95cb Isochrone/isochrone.py  (Katharina Demmich 2022-10-24 16:17:37 +0200  32)                     lats1, lons1, azi1, s12: (M, N) arrays, N=headings+1, M=number of steps+1 (decreasing step number)
919d95cb Isochrone/isochrone.py  (Katharina Demmich 2022-10-24 16:17:37 +0200  33)                     azi0, s0: (M, 1) vectors without history
919d95cb Isochrone/isochrone.py  (Katharina Demmich 2022-10-24 16:17:37 +0200  34)                     time1: current datetime
919d95cb Isochrone/isochrone.py  (Katharina Demmich 2022-10-24 16:17:37 +0200  35)                     elapsed: complete elapsed timedelta
919d95cb Isochrone/isochrone.py  (Katharina Demmich 2022-10-24 16:17:37 +0200  36)         """
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100  37)     ncount: int  # total number of routing steps
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100  38)     count: int  # current routing step
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100  39)     is_last_step : bool
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100  40)     start: tuple  # lat, lon at start
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100  41)     finish: tuple  # lat, lon at end
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100  42)     gcr_azi: float  # azimut of great circle route
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100  43) 
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100  44)     '''
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100  45)         All variables that are named *_per_step constitute (M,N) arrays, whereby N corresponds to the number of variants (plus 1) and
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100  46)         M corresponds to the number of routing steps.
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100  47)     
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100  48)         At the start of each routing step 'count', the element(s) at the position 'count' of the following arrays correspond to
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100  49)         properties of the point of departure of the respective routing step. This means that for 'count = 0' the elements of
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100  50)         lats_per_step and lons_per_step correspond to the coordinates of the departure point of the whole route. The first 
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100  51)         elements of the attributes 
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100  52)             - azimuth_per_step
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100  53)             - dist_per_step
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100  54)             - speed_per_step
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100  55)         are 0 to satisfy this definition.
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100  56)     '''
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100  57)     lats_per_step: np.ndarray  # lats: (M,N) array, N=headings+1, M=steps (M decreasing)    #
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100  58)     lons_per_step: np.ndarray  # longs: (M,N) array, N=headings+1, M=steps
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100  59)     azimuth_per_step: np.ndarray    # heading
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100  60)     dist_per_step: np.ndarray  # geodesic distance traveled per time stamp:
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100  61)     speed_per_step: np.ndarray  # boat speed
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100  62)     fuel_per_step: np.ndarray
49c3d1c8 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-18 14:27:28 +0100  63)     starttime_per_step: np.ndarray
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100  64) 
0ae033dc Isochrone/isochrone.py  (Katharina Demmich 2022-11-03 14:58:28 +0100  65)     current_azimuth: np.ndarray  # current azimuth
0ae033dc Isochrone/isochrone.py  (Katharina Demmich 2022-11-03 14:58:28 +0100  66)     current_variant: np.ndarray  # current variant
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100  67) 
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100  68)     #the lenght of the following arrays depends on the number of variants (variant segments)
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100  69)     full_dist_traveled: np.ndarray  # full geodesic distance since start for all variants
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100  70)     full_time_traveled: np.ndarray  # time elapsed since start for all variants
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100  71)     full_fuel_consumed: np.ndarray
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100  72)     time: np.ndarray                # current datetime for all variants
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100  73) 
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100  74)     variant_segments: int  # number of variant segments in the range of -180° to 180°
fbe1ac36 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 14:34:47 +0100  75)     variant_increments_deg: int
fbe1ac36 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 14:34:47 +0100  76)     expected_speed_kts: int
fbe1ac36 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 14:34:47 +0100  77)     prune_sector_deg_half: int  # angular range of azimuth that is considered for pruning (only one half)
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100  78)     prune_segments: int  # number of azimuth bins that are used for pruning
fbe1ac36 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 14:34:47 +0100  79) 
2690bf87 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-27 11:13:24 +0100  80)     fig: matplotlib.figure
2690bf87 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-27 11:13:24 +0100  81)     route_ensemble : list
2690bf87 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-27 11:13:24 +0100  82)     figure_path : str
d44e737a Isochrone/isochrone.py  (Katharina Demmich 2022-11-14 15:53:33 +0100  83) 
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100  84)     def __init__(self, start, finish, time, figure_path=""):
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100  85)         self.count = 0
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100  86)         self.start = start
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100  87)         self.finish = finish
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100  88)         self.lats_per_step = np.array([[start[0]]])
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100  89)         self.lons_per_step = np.array([[start[1]]])
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100  90)         self.azimuth_per_step = np.array([[None]])
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100  91)         self.dist_per_step = np.array([[0]])
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100  92)         self.speed_per_step = np.array([[0]])
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100  93)         self.fuel_per_step = np.array([[0]])
49c3d1c8 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-18 14:27:28 +0100  94)         self.starttime_per_step = np.array([[time]])
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100  95) 
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100  96)         self.time = np.array([time])
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100  97)         self.full_time_traveled = np.array([0])
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100  98)         self.full_fuel_consumed = np.array([0])
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100  99)         self.full_dist_traveled = np.array([0])
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 100) 
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 101)         gcr = self.calculate_gcr(start, finish)
0ae033dc Isochrone/isochrone.py  (Katharina Demmich 2022-11-03 14:58:28 +0100 102)         self.current_azimuth = gcr
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 103)         self.gcr_azi = gcr
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 104) 
2690bf87 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-27 11:13:24 +0100 105)         self.figure_path = figure_path
2690bf87 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-27 11:13:24 +0100 106) 
d8ab9da6 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-26 12:48:24 +0100 107)         self.print_init()
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 108) 
2690bf87 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-27 11:13:24 +0100 109)     def init_fig(self):
2690bf87 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-27 11:13:24 +0100 110)         pass
2690bf87 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-27 11:13:24 +0100 111) 
2690bf87 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-27 11:13:24 +0100 112)     def update_fig(self):
2690bf87 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-27 11:13:24 +0100 113)         pass
d44e737a Isochrone/isochrone.py  (Katharina Demmich 2022-11-14 15:53:33 +0100 114) 
d8ab9da6 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-26 12:48:24 +0100 115)     def print_init(self):
d8ab9da6 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-26 12:48:24 +0100 116)         logger.info('Initialising routing:')
d8ab9da6 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-26 12:48:24 +0100 117)         logger.info(ut.get_log_step('route from ' + str(self.start) + ' to ' + str(self.finish),1))
d8ab9da6 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-26 12:48:24 +0100 118)         logger.info(ut.get_log_step('start time ' + str(self.time),1))
d8ab9da6 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-26 12:48:24 +0100 119) 
0ae033dc Isochrone/isochrone.py  (Katharina Demmich 2022-11-03 14:58:28 +0100 120)     def print_ra(self):
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 121)         print('PRINTING ALG SETTINGS')
bf47388f Isochrone/isochrone.py  (Katharina Demmich 2022-11-03 11:34:22 +0100 122)         print('step = ', self.count)
0ae033dc Isochrone/isochrone.py  (Katharina Demmich 2022-11-03 14:58:28 +0100 123)         print('start', self.start)
0ae033dc Isochrone/isochrone.py  (Katharina Demmich 2022-11-03 14:58:28 +0100 124)         print('finish', self.finish)
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 125)         print('per-step variables:')
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 126)         print('     lats_per_step = ', self.lats_per_step)
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 127)         print('     lons_per_step = ', self.lons_per_step)
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 128)         print('     variants = ', self.azimuth_per_step)
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 129)         print('     dist_per_step = ', self.dist_per_step)
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 130)         print('     speed_per_step = ', self.speed_per_step)
49c3d1c8 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-18 14:27:28 +0100 131)         print('     starttime_per_step = ', self.starttime_per_step)
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 132)         print('per-variant variables')
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 133)         print('     time =', self.time)
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 134)         print('     full_dist_traveled = ', self.full_dist_traveled)
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 135)         print('     full_time_traveled = ', self.full_time_traveled)
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 136)         print('     full_fuel_consumed = ', self.full_fuel_consumed )
bf47388f Isochrone/isochrone.py  (Katharina Demmich 2022-11-03 11:34:22 +0100 137) 
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 138)     def print_shape(self):
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 139)         print('PRINTING SHAPE')
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 140)         print('per-step variables:')
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 141)         print('     lats_per_step = ', self.lats_per_step.shape)
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 142)         print('     lons_per_step = ', self.lons_per_step.shape)
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 143)         print('     fuel_per_step =', self.fuel_per_step.shape)
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 144)         print('     azimuths = ', self.azimuth_per_step.shape)
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 145)         print('     dist_per_step = ', self.dist_per_step.shape)
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 146)         print('per-variant variables:')
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 147)         print('     time =', self.time.shape)
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 148)         print('     full_dist_traveled = ', self.full_dist_traveled.shape)
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 149)         print('     full_time_traveled = ', self.full_time_traveled.shape)
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 150)         print('     full_fuel_consumed = ', self.full_fuel_consumed.shape)
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 151) 
98398ebe Isochrone/isochrone.py  (Katharina Demmich 2022-11-10 15:39:24 +0100 152)     def current_position(self):
98398ebe Isochrone/isochrone.py  (Katharina Demmich 2022-11-10 15:39:24 +0100 153)         print('CURRENT POSITION')
98398ebe Isochrone/isochrone.py  (Katharina Demmich 2022-11-10 15:39:24 +0100 154)         print('lats = ', self.current_lats)
98398ebe Isochrone/isochrone.py  (Katharina Demmich 2022-11-10 15:39:24 +0100 155)         print('lons = ', self.current_lons)
98398ebe Isochrone/isochrone.py  (Katharina Demmich 2022-11-10 15:39:24 +0100 156)         print('azimuth = ', self.current_azimuth)
98398ebe Isochrone/isochrone.py  (Katharina Demmich 2022-11-10 15:39:24 +0100 157)         print('full_time_traveled = ', self.full_time_traveled)
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 158) 
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 159)     def set_steps(self, steps):
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 160)         self.ncount = steps
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 161) 
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 162)     def calculate_gcr(self, start, finish):
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 163)         gcr = geod.inverse([start[0]], [start[1]], [finish[0]], [
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 164)             finish[1]])  # calculate distance between start and end according to Vincents approach, return dictionary
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 165)         return gcr['azi1']
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 166) 
5a9a4ed8 Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-18 15:27:09 +0100 167)     def get_current_lats(self):
5a9a4ed8 Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-18 15:27:09 +0100 168)         pass
5a9a4ed8 Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-18 15:27:09 +0100 169) 
5a9a4ed8 Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-18 15:27:09 +0100 170)     def get_current_lons(self):
5a9a4ed8 Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-18 15:27:09 +0100 171)         pass
5a9a4ed8 Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-18 15:27:09 +0100 172) 
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 173)     def get_current_speed(self):
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 174)         pass
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 175) 
b367a683 Isochrone/RoutingAlg.py (Katharina Demmich 2022-12-16 11:45:23 +0100 176)     def recursive_routing(self, boat: Boat, wt : WeatherCond, constraints_list : ConstraintsList, verbose=False):
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 177)         """
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 178)             Progress one isochrone with pruning/optimising route for specific time segment
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 179) 
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 180)                     Parameters:
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 181)                         iso1 (Isochrone) - starting isochrone
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 182)                         start_point (tuple) - starting point of the route
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 183)                         end_point (tuple) - end point of the route
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 184)                         x1_coords (tuple) - tuple of arrays (lats, lons)
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 185)                         x2_coords (tuple) - tuple of arrays (lats, lons)
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 186)                         boat (dict) - boat profile
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 187)                         winds (dict) - wind functions
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 188)                         start_time (datetime) - start time
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 189)                         delta_time (float) - time to move in seconds
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 190)                         params (dict) - isochrone calculation parameters
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 191) 
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 192)                     Returns:
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 193)                         iso (Isochrone) - next isochrone
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 194)             """
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 195)         self.check_settings()
fd1e6e90 Isochrone/isochrone.py  (Katharina Demmich 2022-11-07 14:34:14 +0100 196)         self.define_initial_variants()
d7e57cbe Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-11 14:33:41 +0100 197)         #start_time=time.time()
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 198)         # self.print_shape()
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 199)         for i in range(self.ncount):
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 200)             utils.print_line()
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 201)             print('Step ', i)
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 202) 
fd1e6e90 Isochrone/isochrone.py  (Katharina Demmich 2022-11-07 14:34:14 +0100 203)             self.define_variants_per_step()
b367a683 Isochrone/RoutingAlg.py (Katharina Demmich 2022-12-16 11:45:23 +0100 204)             self.move_boat_direct(wt, boat, constraints_list)
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 205)             if(self.is_last_step):
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 206)                 logger.info('Initiating last step at routing step ' + str(self.count))
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 207)                 break
6b489495 Isochrone/RoutingAlg.py (Katharina Demmich 2023-02-07 11:33:43 +0100 208)             #self.update_fig('bp')
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 209)             self.pruning_per_step(True)
d7e57cbe Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-11 14:33:41 +0100 210)             #ut.print_current_time('move_boat: Step=' + str(i), start_time)
a4e90f49 Isochrone/RoutingAlg.py (Katharina Demmich 2023-03-01 14:36:30 +0100 211)             self.update_fig('p')
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 212) 
fd1e6e90 Isochrone/isochrone.py  (Katharina Demmich 2022-11-07 14:34:14 +0100 213)         self.final_pruning()
de5a5224 Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 16:56:47 +0100 214)         route = self.terminate(boat, wt)
a4e90f49 Isochrone/RoutingAlg.py (Katharina Demmich 2023-03-01 14:36:30 +0100 215)         return route
d44e737a Isochrone/isochrone.py  (Katharina Demmich 2022-11-14 15:53:33 +0100 216) 
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 217) 
fbe1ac36 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 14:34:47 +0100 218)     def define_variants(self):
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 219)         # branch out for multiple headings
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 220)         nof_input_routes = self.lats_per_step.shape[1]
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 221) 
fbe1ac36 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 14:34:47 +0100 222)         self.lats_per_step = np.repeat(self.lats_per_step, self.variant_segments + 1, axis=1)
fbe1ac36 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 14:34:47 +0100 223)         self.lons_per_step = np.repeat(self.lons_per_step, self.variant_segments + 1, axis=1)
fbe1ac36 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 14:34:47 +0100 224)         self.dist_per_step = np.repeat(self.dist_per_step, self.variant_segments + 1, axis=1)
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 225)         self.azimuth_per_step = np.repeat(self.azimuth_per_step, self.variant_segments + 1, axis=1)
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100 226)         self.speed_per_step = np.repeat(self.speed_per_step, self.variant_segments + 1, axis=1)
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 227)         self.fuel_per_step = np.repeat(self.fuel_per_step, self.variant_segments + 1, axis=1)
49c3d1c8 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-18 14:27:28 +0100 228)         self.starttime_per_step = np.repeat(self.starttime_per_step, self.variant_segments + 1, axis=1)
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 229) 
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 230)         self.full_time_traveled = np.repeat(self.full_time_traveled, self.variant_segments + 1, axis=0)
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 231)         self.full_fuel_consumed = np.repeat(self.full_fuel_consumed, self.variant_segments + 1, axis=0)
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 232)         self.full_dist_traveled = np.repeat(self.full_dist_traveled, self.variant_segments + 1, axis=0)
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 233)         self.time = np.repeat(self.time, self.variant_segments + 1, axis=0)
fd1e6e90 Isochrone/isochrone.py  (Katharina Demmich 2022-11-07 14:34:14 +0100 234)         self.check_variant_def()
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 235) 
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 236)         # determine new headings - centered around gcrs X0 -> X_prev_step
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 237)         delta_hdgs = np.linspace(
0bc35f87 Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-18 11:57:50 +0100 238)             -self.variant_segments/2 * self.variant_increments_deg,
0bc35f87 Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-18 11:57:50 +0100 239)             +self.variant_segments/2 * self.variant_increments_deg,
0e1b4174 Isochrone/RoutingAlg.py (Katharina Demmich 2022-12-15 10:42:52 +0100 240)             self.variant_segments + 1)
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 241)         delta_hdgs = np.tile(delta_hdgs, nof_input_routes)
fd1e6e90 Isochrone/isochrone.py  (Katharina Demmich 2022-11-07 14:34:14 +0100 242)         self.current_variant = np.repeat(self.current_variant, self.variant_segments + 1)
fd1e6e90 Isochrone/isochrone.py  (Katharina Demmich 2022-11-07 14:34:14 +0100 243)         self.current_variant = self.current_variant - delta_hdgs
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 244) 
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 245)     def define_initial_variants(self):
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 246)         pass
8f0fb4dd Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 15:57:58 +0100 247) 
b367a683 Isochrone/RoutingAlg.py (Katharina Demmich 2022-12-16 11:45:23 +0100 248)     def move_boat_direct(self, wt : WeatherCond, boat: Boat, constraint_list: ConstraintsList):
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 249)         """
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 250)                 calculate new boat position for current time step based on wind and boat function
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 251)             """
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 252) 
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 253)         # get wind speed (tws) and angle (twa)
e2bf2f20 Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 15:22:57 +0100 254)         debug = False
98398ebe Isochrone/isochrone.py  (Katharina Demmich 2022-11-10 15:39:24 +0100 255) 
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100 256)         winds = self.get_wind_functions(wt) #wind is always a function of the variants
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 257)         twa = winds['twa']
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 258)         tws = winds['tws']
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 259)         wind = {'tws': tws, 'twa': twa - self.get_current_azimuth()}
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 260)         #if(debug) : print('wind in move_boat_direct', wind)
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 261) 
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 262)         # get boat speed
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 263)         bs = boat.boat_speed_function(wind)
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100 264)         self.speed_per_step = np.vstack((bs, self.speed_per_step))
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 265) 
97339e51 Isochrone/RoutingAlg.py (Katharina Demmich 2022-12-09 15:27:31 +0100 266)         #delta_time, delta_fuel, dist = self.get_delta_variables(boat,wind,bs)
97339e51 Isochrone/RoutingAlg.py (Katharina Demmich 2022-12-09 15:27:31 +0100 267)         delta_time, delta_fuel, dist = self.get_delta_variables_netCDF(boat, wind, bs)
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 268)         if (debug):
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 269)             print('delta_time: ', delta_time)
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 270)             print('delta_fuel: ', delta_fuel)
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 271)             print('dist: ', dist)
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 272)             print('is_last_step:', self.is_last_step)
5a9a4ed8 Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-18 15:27:09 +0100 273) 
b367a683 Isochrone/RoutingAlg.py (Katharina Demmich 2022-12-16 11:45:23 +0100 274)         move = self.check_bearing(dist)
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 275) 
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 276)         if (debug):
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 277)             print('move:', move)
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 278) 
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 279)         if(self.is_last_step):
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 280)             delta_time, delta_fuel, dist = self.get_delta_variables_netCDF_last_step(boat, wind, bs)
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 281) 
b367a683 Isochrone/RoutingAlg.py (Katharina Demmich 2022-12-16 11:45:23 +0100 282)         is_constrained = self.check_constraints(move, constraint_list)
b367a683 Isochrone/RoutingAlg.py (Katharina Demmich 2022-12-16 11:45:23 +0100 283) 
b367a683 Isochrone/RoutingAlg.py (Katharina Demmich 2022-12-16 11:45:23 +0100 284)         self.update_position(move, is_constrained, dist)
5a9a4ed8 Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-18 15:27:09 +0100 285)         self.update_time(delta_time)
5a9a4ed8 Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-18 15:27:09 +0100 286)         self.update_fuel(delta_fuel)
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 287)         self.count += 1
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 288) 
de5a5224 Isochrone/RoutingAlg.py (Katharina Demmich 2022-11-22 16:56:47 +0100 289)     def terminate(self, boat: Boat, wt: WeatherCond):
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 290)         utils.print_line()
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 291)         print('Terminating...')
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 292) 
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 293)         time = round(self.full_time_traveled / 3600,2 )
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 294)         route = RouteParams(
6b489495 Isochrone/RoutingAlg.py (Katharina Demmich 2023-02-07 11:33:43 +0100 295)             count = self.count,  # routing step
6b489495 Isochrone/RoutingAlg.py (Katharina Demmich 2023-02-07 11:33:43 +0100 296)             start = self.start,  # lat, lon at start
6b489495 Isochrone/RoutingAlg.py (Katharina Demmich 2023-02-07 11:33:43 +0100 297)             finish = self.finish,  # lat, lon at end
6b489495 Isochrone/RoutingAlg.py (Katharina Demmich 2023-02-07 11:33:43 +0100 298)             fuel = self.full_fuel_consumed / (3600 * 1000),  # sum of fuel consumption [kWh]
6b489495 Isochrone/RoutingAlg.py (Katharina Demmich 2023-02-07 11:33:43 +0100 299)             full_dist_traveled=np.sum(self.dist_per_step), # [m]
6b489495 Isochrone/RoutingAlg.py (Katharina Demmich 2023-02-07 11:33:43 +0100 300)             gcr = self.full_dist_traveled, #[m]
6b489495 Isochrone/RoutingAlg.py (Katharina Demmich 2023-02-07 11:33:43 +0100 301)             rpm = boat.get_rpm(),  # propeller [revolutions per minute]
6b489495 Isochrone/RoutingAlg.py (Katharina Demmich 2023-02-07 11:33:43 +0100 302)             route_type = 'min_time_route',  # route name
6b489495 Isochrone/RoutingAlg.py (Katharina Demmich 2023-02-07 11:33:43 +0100 303)             time = time,  # time needed for the route [h]
6b489495 Isochrone/RoutingAlg.py (Katharina Demmich 2023-02-07 11:33:43 +0100 304)             lats_per_step = self.lats_per_step[:],
6b489495 Isochrone/RoutingAlg.py (Katharina Demmich 2023-02-07 11:33:43 +0100 305)             lons_per_step = self.lons_per_step[:],
6b489495 Isochrone/RoutingAlg.py (Katharina Demmich 2023-02-07 11:33:43 +0100 306)             azimuths_per_step = self.azimuth_per_step[:],
6b489495 Isochrone/RoutingAlg.py (Katharina Demmich 2023-02-07 11:33:43 +0100 307)             dists_per_step = self.dist_per_step[:], #[m]
6b489495 Isochrone/RoutingAlg.py (Katharina Demmich 2023-02-07 11:33:43 +0100 308)             speed_per_step = self.speed_per_step[:],
6b489495 Isochrone/RoutingAlg.py (Katharina Demmich 2023-02-07 11:33:43 +0100 309)             starttime_per_step = self.starttime_per_step[:],
6b489495 Isochrone/RoutingAlg.py (Katharina Demmich 2023-02-07 11:33:43 +0100 310)             fuel_per_step = self.fuel_per_step[:] / (3600 * 1000),  # fuel consumption [kWh] per step
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 311)         )
0396148c Isochrone/isochrone.py  (Katharina Demmich 2022-11-15 11:57:08 +0100 312)         #route.print_route()
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 313)         self.check_destination()
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 314)         self.check_positive_power()
aa93e115 Isochrone/isochrone.py  (Katharina Demmich 2022-11-02 10:34:14 +0100 315)         return route
fd1e6e90 Isochrone/isochrone.py  (Katharina Demmich 2022-11-07 14:34:14 +0100 316) 
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 317)     def check_destination(self):
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 318)         destination_lats = self.lats_per_step[self.lats_per_step.shape[0]-1]
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 319)         destination_lons = self.lons_per_step[self.lons_per_step.shape[0]-1]
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 320) 
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 321)         arrived_at_destination = (destination_lats==self.finish[0]) & (destination_lons == self.finish[1])
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 322)         if not arrived_at_destination:
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 323)             logger.error('Did not arrive at destination! Need further routing steps or lower resolution.')
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 324) 
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 325)     def check_positive_power(self):
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 326)         negative_power = self.full_fuel_consumed<0
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 327)         if negative_power.any():
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 328)             logging.error('Have negative values for power consumption. Needs to be checked!')
2aee2b40 Isochrone/RoutingAlg.py (Katharina Demmich 2023-01-30 17:29:10 +0100 329) 
fd1e6e90 Isochrone/isochrone.py  (Katharina Demmich 2022-11-07 14:34:14 +0100 330)     def check_variant_def(self):
fd1e6e90 Isochrone/isochrone.py  (Katharina Demmich 2022-11-07 14:34:14 +0100 331)         pass
fd1e6e90 Isochrone/isochrone.py  (Katharina Demmich 2022-11-07 14:34:14 +0100 332) 
fd1e6e90 Isochrone/isochrone.py  (Katharina Demmich 2022-11-07 14:34:14 +0100 333)     def define_variants_per_step(self):
fd1e6e90 Isochrone/isochrone.py  (Katharina Demmich 2022-11-07 14:34:14 +0100 334)         pass
fd1e6e90 Isochrone/isochrone.py  (Katharina Demmich 2022-11-07 14:34:14 +0100 335) 
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 336)     def pruning_per_step(self, trim=True):
fd1e6e90 Isochrone/isochrone.py  (Katharina Demmich 2022-11-07 14:34:14 +0100 337)         pass
fd1e6e90 Isochrone/isochrone.py  (Katharina Demmich 2022-11-07 14:34:14 +0100 338) 
fd1e6e90 Isochrone/isochrone.py  (Katharina Demmich 2022-11-07 14:34:14 +0100 339)     def final_pruning(self):
fd1e6e90 Isochrone/isochrone.py  (Katharina Demmich 2022-11-07 14:34:14 +0100 340)         pass
fd1e6e90 Isochrone/isochrone.py  (Katharina Demmich 2022-11-07 14:34:14 +0100 341) 
fd1e6e90 Isochrone/isochrone.py  (Katharina Demmich 2022-11-07 14:34:14 +0100 342)     def get_current_azimuth(self):
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 343)         pass
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 344) 
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 345)     def update_dist(self, delta_time, bs):
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 346)         pass
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 347) 
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 348)     def update_time(self, delta_time, bs, current_lats, current_lons):
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 349)         pass
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 350) 
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 351)     def get_final_index(self):
78f34efc Isochrone/isochrone.py  (Katharina Demmich 2022-11-08 15:23:02 +0100 352)         pass
