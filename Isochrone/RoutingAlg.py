import numpy as np
import datetime as dt
import utils as ut
import time

from polars import Boat
from typing import NamedTuple
from geovectorslib import geod
from weather import WeatherCond
from global_land_mask import globe
from scipy.stats import binned_statistic
from routeparams import RouteParams
import matplotlib
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import graphics
import logging

import utils
from Constraints import *

logger = logging.getLogger('WRT.routingalg')

class RoutingAlg():
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
    ncount: int  # total number of routing steps
    count: int  # current routing step
    start: tuple  # lat, lon at start
    finish: tuple  # lat, lon at end
    gcr_azi: float  # azimut of great circle route

    '''
        All variables that are named *_per_step constitute (M,N) arrays, whereby N corresponds to the number of variants (plus 1) and
        M corresponds to the number of routing steps.
    
        At the start of each routing step 'count', the element(s) at the position 'count' of the following arrays correspond to
        properties of the point of departure of the respective routing step. This means that for 'count = 0' the elements of
        lats_per_step and lons_per_step correspond to the coordinates of the departure point of the whole route. The first 
        elements of the attributes 
            - azimuth_per_step
            - dist_per_step
            - speed_per_step
        are 0 to satisfy this definition.
    '''
    lats_per_step: np.ndarray  # lats: (M,N) array, N=headings+1, M=steps (M decreasing)    #
    lons_per_step: np.ndarray  # longs: (M,N) array, N=headings+1, M=steps
    azimuth_per_step: np.ndarray    # heading
    dist_per_step: np.ndarray  # geodesic distance traveled per time stamp:
    speed_per_step: np.ndarray  # boat speed
    fuel_per_step: np.ndarray
    starttime_per_step: np.ndarray

    current_azimuth: np.ndarray  # current azimuth
    current_variant: np.ndarray  # current variant

    #the lenght of the following arrays depends on the number of variants (variant segments)
    full_dist_traveled: np.ndarray  # full geodesic distance since start for all variants
    full_time_traveled: np.ndarray  # time elapsed since start for all variants
    full_fuel_consumed: np.ndarray
    time: np.ndarray                # current datetime for all variants

    variant_segments: int  # number of variant segments in the range of -180° to 180°
    variant_increments_deg: int
    expected_speed_kts: int
    prune_sector_deg_half: int  # angular range of azimuth that is considered for pruning (only one half)
    prune_segments: int  # number of azimuth bins that are used for pruning

    fig: matplotlib.figure
    route_ensemble : list
    figure_path : str

    def __init__(self, start, finish, time, figure_path):
        self.count = 0
        self.start = start
        self.finish = finish
        self.lats_per_step = np.array([[start[0]]])
        self.lons_per_step = np.array([[start[1]]])
        self.azimuth_per_step = np.array([[None]])
        self.dist_per_step = np.array([[0]])
        self.speed_per_step = np.array([[0]])
        self.fuel_per_step = np.array([[0]])
        self.starttime_per_step = np.array([[time]])

        self.time = np.array([time])
        self.full_time_traveled = np.array([0])
        self.full_fuel_consumed = np.array([0])
        self.full_dist_traveled = np.array([0])

        gcr = self.calculate_gcr(start, finish)
        self.current_azimuth = gcr
        self.gcr_azi = gcr

        self.figure_path = figure_path

        self.print_init()

    def init_fig(self):
        pass

    def update_fig(self):
        pass

    def print_init(self):
        logger.info('Initialising routing:')
        logger.info(ut.get_log_step('route from ' + str(self.start) + ' to ' + str(self.finish),1))
        logger.info(ut.get_log_step('start time ' + str(self.time),1))

    def print_ra(self):
        print('PRINTING ALG SETTINGS')
        print('step = ', self.count)
        print('start', self.start)
        print('finish', self.finish)
        print('per-step variables:')
        print('     lats_per_step = ', self.lats_per_step)
        print('     lons_per_step = ', self.lons_per_step)
        print('     variants = ', self.azimuth_per_step)
        print('     dist_per_step = ', self.dist_per_step)
        print('     speed_per_step = ', self.speed_per_step)
        print('     starttime_per_step = ', self.starttime_per_step)
        print('per-variant variables')
        print('     time =', self.time)
        print('     full_dist_traveled = ', self.full_dist_traveled)
        print('     full_time_traveled = ', self.full_time_traveled)
        print('     full_fuel_consumed = ', self.full_fuel_consumed )

    def print_shape(self):
        print('PRINTING SHAPE')
        print('per-step variables:')
        print('     lats_per_step = ', self.lats_per_step.shape)
        print('     lons_per_step = ', self.lons_per_step.shape)
        print('     fuel_per_step =', self.fuel_per_step.shape)
        print('     azimuths = ', self.azimuth_per_step.shape)
        print('     dist_per_step = ', self.dist_per_step.shape)
        print('per-variant variables:')
        print('     time =', self.time.shape)
        print('     full_dist_traveled = ', self.full_dist_traveled.shape)
        print('     full_time_traveled = ', self.full_time_traveled.shape)
        print('     full_fuel_consumed = ', self.full_fuel_consumed.shape)

    def current_position(self):
        print('CURRENT POSITION')
        print('lats = ', self.current_lats)
        print('lons = ', self.current_lons)
        print('azimuth = ', self.current_azimuth)
        print('full_time_traveled = ', self.full_time_traveled)

    def set_steps(self, steps):
        self.ncount = steps

    def calculate_gcr(self, start, finish):
        gcr = geod.inverse([start[0]], [start[1]], [finish[0]], [
            finish[1]])  # calculate distance between start and end according to Vincents approach, return dictionary
        return gcr['azi1']

    def get_current_lats(self):
        pass

    def get_current_lons(self):
        pass

    def get_current_speed(self):
        pass

    def recursive_routing(self, boat: Boat, wt : WeatherCond, constraints_list : ConstraintsList, verbose=False):
        """
            Progress one isochrone with pruning/optimising route for specific time segment

                    Parameters:
                        iso1 (Isochrone) - starting isochrone
                        start_point (tuple) - starting point of the route
                        end_point (tuple) - end point of the route
                        x1_coords (tuple) - tuple of arrays (lats, lons)
                        x2_coords (tuple) - tuple of arrays (lats, lons)
                        boat (dict) - boat profile
                        winds (dict) - wind functions
                        start_time (datetime) - start time
                        delta_time (float) - time to move in seconds
                        params (dict) - isochrone calculation parameters

                    Returns:
                        iso (Isochrone) - next isochrone
            """
        self.check_settings()
        self.define_initial_variants()
        #start_time=time.time()
        # self.print_shape()
        for i in range(self.ncount):
            utils.print_line()
            print('Step ', i)

            self.define_variants_per_step()
            self.move_boat_direct(wt, boat, constraints_list)
            self.pruning_per_step(True)
            #ut.print_current_time('move_boat: Step=' + str(i), start_time)
            self.update_fig()

        self.final_pruning()
        route = self.terminate(boat, wt)
        return {'route' : route, 'fig' : self.fig}


    def define_variants(self):
        # branch out for multiple headings
        nof_input_routes = self.lats_per_step.shape[1]

        self.lats_per_step = np.repeat(self.lats_per_step, self.variant_segments + 1, axis=1)
        self.lons_per_step = np.repeat(self.lons_per_step, self.variant_segments + 1, axis=1)
        self.dist_per_step = np.repeat(self.dist_per_step, self.variant_segments + 1, axis=1)
        self.azimuth_per_step = np.repeat(self.azimuth_per_step, self.variant_segments + 1, axis=1)
        self.speed_per_step = np.repeat(self.speed_per_step, self.variant_segments + 1, axis=1)
        self.fuel_per_step = np.repeat(self.fuel_per_step, self.variant_segments + 1, axis=1)
        self.starttime_per_step = np.repeat(self.starttime_per_step, self.variant_segments + 1, axis=1)

        self.full_time_traveled = np.repeat(self.full_time_traveled, self.variant_segments + 1, axis=0)
        self.full_fuel_consumed = np.repeat(self.full_fuel_consumed, self.variant_segments + 1, axis=0)
        self.full_dist_traveled = np.repeat(self.full_dist_traveled, self.variant_segments + 1, axis=0)
        self.time = np.repeat(self.time, self.variant_segments + 1, axis=0)
        self.check_variant_def()

        # determine new headings - centered around gcrs X0 -> X_prev_step
        delta_hdgs = np.linspace(
            -self.variant_segments/2 * self.variant_increments_deg,
            +self.variant_segments/2 * self.variant_increments_deg,
            self.variant_segments + 1)
        delta_hdgs = np.tile(delta_hdgs, nof_input_routes)
        self.current_variant = np.repeat(self.current_variant, self.variant_segments + 1)
        self.current_variant = self.current_variant - delta_hdgs

    def define_initial_variants(self):
        pass

    def move_boat_direct(self, wt : WeatherCond, boat: Boat, constraint_list: ConstraintsList):
        """
                calculate new boat position for current time step based on wind and boat function
            """

        # get wind speed (tws) and angle (twa)
        debug = False

        winds = self.get_wind_functions(wt) #wind is always a function of the variants
        twa = winds['twa']
        tws = winds['tws']
        wind = {'tws': tws, 'twa': twa - self.get_current_azimuth()}
        if(debug) : print('wind in move_boat_direct', wind)

        # get boat speed
        bs = boat.boat_speed_function(wind)
        self.speed_per_step = np.vstack((bs, self.speed_per_step))

        #delta_time, delta_fuel, dist = self.get_delta_variables(boat,wind,bs)
        delta_time, delta_fuel, dist = self.get_delta_variables_netCDF(boat, wind, bs)

        move = self.check_bearing(dist)
        is_constrained = self.check_constraints(move, constraint_list)

        self.update_position(move, is_constrained, dist)
        self.update_time(delta_time)
        self.update_fuel(delta_fuel)
        self.count += 1

    def terminate(self, boat: Boat, wt: WeatherCond):
        utils.print_line()
        print('Terminating...')

        idx = self.get_final_index()
        time = round(self.full_time_traveled[idx] / 3600,2 )

        route = RouteParams(
            self.count,  # routing step
            self.start,  # lat, lon at start
            self.finish,  # lat, lon at end
            self.full_fuel_consumed[idx],  # sum of fuel consumption [t]
            boat.get_rpm(),  # propeller [revolutions per minute]
            'min_time_route',  # route name
            time,  # time needed for the route [seconds]
            self.lats_per_step[:, idx],
            self.lons_per_step[:, idx],
            self.azimuth_per_step[:, idx],
            self.dist_per_step[:, idx],
            self.speed_per_step[:, idx],
            self.starttime_per_step[:, idx],
            self.full_dist_traveled[idx]
        )
        #route.print_route()

        return route

    def check_variant_def(self):
        pass

    def define_variants_per_step(self):
        pass

    def pruning_per_step(self, trim=True):
        pass

    def final_pruning(self):
        pass

    def get_current_azimuth(self):
        pass

    def update_dist(self, delta_time, bs):
        pass

    def update_time(self, delta_time, bs, current_lats, current_lons):
        pass

    def get_final_index(self):
        pass
