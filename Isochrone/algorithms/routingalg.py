import datetime as dt
import logging
import time

import numpy as np
import matplotlib
from geovectorslib import geod
from matplotlib.axes import Axes
from matplotlib.figure import Figure

import utils.formatting as form
from constraints.constraints import *
from ship.ship import Boat
from routeparams import RouteParams
from weather import WeatherCond

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

    fig: matplotlib.figure
    route_ensemble : list
    figure_path : str

    def __init__(self, start, finish, figure_path=""):
        self.count = 0
        self.start = start
        self.finish = finish

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
        logger.info(form.get_log_step('route from ' + str(self.start) + ' to ' + str(self.finish),1))
        logger.info(form.get_log_step('start time ' + str(self.time),1))

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
        print('     starttime_per_step = ', self.starttime_per_step)

        self.shipparams_per_step.print()

        print('per-variant variables')
        print('     time =', self.time)
        print('     full_dist_traveled = ', self.full_dist_traveled)
        print('     full_time_traveled = ', self.full_time_traveled)
        print('     full_fuel_consumed = ', self.full_fuel_consumed )

    def set_steps(self, steps):
        self.ncount = steps

    def calculate_gcr(self, start, finish):
        gcr = geod.inverse([start[0]], [start[1]], [finish[0]], [
            finish[1]])  # calculate distance between start and end according to Vincents approach, return dictionary
        return gcr['azi1']

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
        self.check_for_positive_constraints(constraints_list)
        self.define_initial_variants()
        #start_time=time.time()
        # self.print_shape()
        for i in range(self.ncount):
            form.print_line()
            print('Step ', i)

            self.define_variants_per_step()
            self.move_boat_direct(wt, boat, constraints_list)
            if self.is_last_step:
                logger.info('Initiating last step at routing step ' + str(self.count))
                break

            if self.is_pos_constraint_step:
                logger.info('Initiating pruning for intermediate waypoint at routing step' + str(self.count))
                self.final_pruning()
                self.expand_axis_for_intermediate()
                constraints_list.reached_positive()
                self.finish_temp = constraints_list.get_current_destination()
                self.start_temp = constraints_list.get_current_start()
                self.gcr_azi_temp = self.calculate_gcr(self.start_temp, self.finish_temp)
                self.is_pos_constraint_step = False

                logger.info('Initiating routing for next segment going from ' + str(self.start_temp) + ' to ' + str(self.finish_temp))
                continue

            #if i>9:
            #self.update_fig('bp')
            self.pruning_per_step(True)
            #form.print_current_time('move_boat: Step=' + str(i), start_time)
            #if i>9:
            #self.update_fig('p')

        self.final_pruning()
        route = self.terminate(boat, wt)
        return route

    def check_for_positive_constraints(self, constraint_list):
        have_pos_points = constraint_list.have_positive()
        if not have_pos_points:
            self.finish_temp = self.finish
            self.start_temp = self.start
            return

        constraint_list.init_positive_lists(self.start, self.finish)
        self.finish_temp = constraint_list.get_current_destination()
        self.start_temp = constraint_list.get_current_start()
        self.gcr_azi_temp = self.calculate_gcr(self.start_temp, self.finish_temp)

        print('Currently going from')
        print(self.start_temp)
        print('to')
        print(self.finish_temp)


    def terminate(self, boat: Boat, wt: WeatherCond):
        form.print_line()
        print('Terminating...')

        time = round(self.full_time_traveled / 3600,2 )
        route = RouteParams(
            count = self.count,
            start = self.start,
            finish = self.finish,
            gcr = self.full_dist_traveled,
            route_type = 'min_time_route',
            time = time,
            lats_per_step = self.lats_per_step[:],
            lons_per_step = self.lons_per_step[:],
            azimuths_per_step = self.azimuth_per_step[:],
            dists_per_step = self.dist_per_step[:],
            starttime_per_step = self.starttime_per_step[:],
            ship_params_per_step = self.shipparams_per_step
        )
        #route.print_route()
        self.check_destination()
        self.check_positive_power()
        self.check_gcr()
        return route

    def check_gcr(self):
        gcr_equal_traveldist = (self.full_dist_traveled == np.sum(self.dist_per_step))
        if not gcr_equal_traveldist:
            logger.error('Gcr is not matching travel distance on great circel route summed for all routing steps.')

    def check_destination(self):
        destination_lats = self.lats_per_step[self.lats_per_step.shape[0]-1]
        destination_lons = self.lons_per_step[self.lons_per_step.shape[0]-1]

        arrived_at_destination = (destination_lats==self.finish[0]) & (destination_lons == self.finish[1])
        if not arrived_at_destination:
            logger.error('Did not arrive at destination! Need further routing steps or lower resolution.')

    def check_positive_power(self):
        negative_power = self.full_fuel_consumed<0
        if negative_power.any():
            logging.error('Have negative values for power consumption. Needs to be checked!')

