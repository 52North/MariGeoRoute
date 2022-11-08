import numpy as np
import datetime as dt
import utils as ut
from polars import Boat
from typing import NamedTuple
from geovectorslib import geod
from weather import wind_function
from global_land_mask import globe
from scipy.stats import binned_statistic
from routeparams import RouteParams
import utils


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

    lats_per_step: np.ndarray  # lats: (M,N) array, N=headings+1, M=steps (M decreasing)    #
    lons_per_step: np.ndarray  # longs: (M,N) array, N=headings+1, M=steps                  #
    azimuth_per_step: np.ndarray  # azimuth: (M,N) array, N=headings+1, M=steps
    dist_per_step: np.ndarray  # geodesic distance traveled per time stamp: (M,N) array, N=headings+1, M=steps

    current_lats: np.ndarray
    current_lons: np.ndarray
    current_azimuth: np.ndarray  # current azimuth
    current_variant: np.ndarray  # current variant

    full_dist_traveled: np.ndarray  # full geodesic distance since start
    time: dt.datetime  # current datetime
    full_time_traveled: np.ndarray  # time elapsed since start

    variant_segments: int  # number of variant segments in the range of -180° to 180°
    variant_increments_deg: int
    expected_speed_kts: int
    prune_sector_deg_half: int  # angular range of azimuth that is considered for pruning (only one half)
    prune_segments: int  # number of azimuth bins that are used for pruning

    def __init__(self, start, finish, time):
        self.count = 0
        self.start = start
        self.finish = finish
        self.lats_per_step = np.array([[start[0]]])
        self.lons_per_step = np.array([[start[1]]])
        self.azimuth_per_step = np.array([[None]])
        self.dist_per_step = np.array([[0]])
        self.full_dist_traveled = np.array([])
        self.time = time
        self.full_time_traveled = np.array([])

        self.current_lats = np.array([start[0]])
        self.current_lons = np.array([start[1]])
        gcr = self.calculate_gcr(start, finish)
        self.current_azimuth = gcr
        self.gcr_azi = gcr

        ut.print_line()
        print('Initialising routing: ' + str(start) + ' to ' + str(finish))
        print('     route from ' + str(start) + ' to ' + str(finish))
        print('     start time ' + str(time))

    def print_ra(self):
        print('PRINTING ALG SETTINGS')
        print('step = ', self.count)
        print('start', self.start)
        print('finish', self.finish)
        print('lats_per_step = ', self.lats_per_step)
        print('lons_per_step = ', self.lons_per_step)
        print('variants = ', self.azimuth_per_step)
        print('dist_per_step = ', self.dist_per_step)
        print('full_dist_traveled = ', self.full_dist_traveled)
        print('time = ', self.time)

    def print_shape(self):
        print('PRINTING SHAPE')
        print('lats_per_step = ', self.lats_per_step.shape)
        print('lons_per_step = ', self.lons_per_step.shape)
        print('azimuths = ', self.azimuth_per_step.shape)
        print('dist_per_step = ', self.dist_per_step.shape)
        print('full_dist_traveled = ', self.full_dist_traveled.shape)
        print('full_time_traveled = ', self.full_time_traveled.shape)

    def set_steps(self, steps):
        self.ncount = steps

    def set_variant_segments(self, segments):
        self.variant_segments = segments

    def set_pruning_settings(self, sector_deg_half, seg):
        self.prune_sector_deg_half = sector_deg_half
        self.prune_segments = seg

    def set_variant_segments(self, seg, inc):
        self.variant_segments = seg
        self.variant_increments_deg = inc

    def calculate_gcr(self, start, finish):
        gcr = geod.inverse([start[0]], [start[1]], [finish[0]], [
            finish[1]])  # calculate distance between start and end according to Vincents approach, return dictionary
        return gcr['azi1']

    def recursive_routing(self, boat: Boat, winds, delta_time, verbose=False):
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
        self.define_initial_variants()
        # self.print_shape()
        for i in range(self.ncount):
            utils.print_line()
            print('Step ', i)
            # self.current_position()
            # self.print_shape()
            # self.print_ra()

            self.define_variants_per_step()
            self.move_boat_direct(winds, boat, delta_time)
            self.pruning_per_step(True)

            print('full_time_traveled:', self.full_time_traveled)

        self.final_pruning()
        route = self.terminate(boat)
        return route

    def define_variants(self):
        # branch out for multiple headings
        nof_input_routes = self.lats_per_step.shape[1]

        self.lats_per_step = np.repeat(self.lats_per_step, self.variant_segments + 1, axis=1)
        self.lons_per_step = np.repeat(self.lons_per_step, self.variant_segments + 1, axis=1)
        self.dist_per_step = np.repeat(self.dist_per_step, self.variant_segments + 1, axis=1)
        self.azimuth_per_step = np.repeat(self.azimuth_per_step, self.variant_segments + 1, axis=1)
        self.check_variant_def()

        # determine new headings - centered around gcrs X0 -> X_prev_step
        delta_hdgs = np.linspace(
            -self.variant_segments * self.variant_increments_deg,
            +self.variant_segments * self.variant_increments_deg,
            self.variant_segments + 1)
        delta_hdgs = np.tile(delta_hdgs, nof_input_routes)
        self.current_variant = np.repeat(self.current_variant, self.variant_segments + 1)
        self.current_variant = self.current_variant - delta_hdgs

    def move_boat_direct(self, winds, boat: Boat, delta_time):
        """
                calculate new boat position for current time step based on wind and boat function
            """

        # get wind speed (tws) and angle (twa)
        print('lats', self.current_lats)
        print('lons', self.current_lons)
        print('time', self.time)
        winds = wind_function(winds, (self.current_lats, self.current_lons), self.time)
        twa = winds['twa']
        tws = winds['tws']
        wind = {'tws': tws, 'twa': twa - self.get_current_azimuth()}
        print('twa= ' + str(twa) + 'tws= ' + str(tws))

        # get boat speed
        bs = boat.boat_speed_function(wind)

        # update boat position
        self.update_position()
        self.update_dist(delta_time, bs, self.current_lats, self.current_lons)
        self.update_time(delta_time, bs)
        self.count += 1

    def terminate(self, boat: Boat):
        utils.print_line()
        print('Terminating...')

        idx = self.get_final_index()
        fuel = round(boat.get_fuel_per_time(self.full_time_traveled[idx]), 2)
        time = round(self.full_time_traveled[idx] / 3600,2 )

        route = RouteParams(
            self.count,  # routing step
            self.start,  # lat, lon at start
            self.finish,  # lat, lon at end
            fuel,  # sum of fuel consumption [t]
            boat.get_rpm(),  # propeller [revolutions per minute]
            'min_time_route',  # route name
            time,  # time needed for the route [seconds]
            self.lats_per_step[:, idx],
            self.lons_per_step[:, idx],
            self.azimuth_per_step[:, idx],
            self.dist_per_step[:, idx],
            self.full_dist_traveled[idx]
        )

        route.print_route()

        return route

    def check_variant_def(self):
        pass

    def define_initial_variants(self):
        pass

    def define_variants_per_step(self):
        pass

    def pruning_per_step(self, trim=True):
        pass

    def variants_per_step(self):
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
