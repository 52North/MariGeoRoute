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
from ship.shipparams import ShipParams
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
    is_last_step : bool
    is_pos_constraint_step : bool
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
    start_temp : tuple
    finish_temp : tuple

    lats_per_step: np.ndarray  # lats: (M,N) array, N=headings+1, M=steps (M decreasing)    #
    lons_per_step: np.ndarray  # longs: (M,N) array, N=headings+1, M=steps
    azimuth_per_step: np.ndarray    # heading
    dist_per_step: np.ndarray  # geodesic distance traveled per time stamp:
    shipparams_per_step: ShipParams
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

    def __init__(self, start, finish, time, figure_path=""):
        self.count = 0
        self.start = start
        self.finish = finish
        self.lats_per_step = np.array([[start[0]]])
        self.lons_per_step = np.array([[start[1]]])
        self.azimuth_per_step = np.array([[None]])
        self.dist_per_step = np.array([[0]])
        sp = ShipParams.set_default_array()
        self.shipparams_per_step = sp
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

    def print_shape(self):
        print('PRINTING SHAPE')
        print('per-step variables:')
        print('     lats_per_step = ', self.lats_per_step.shape)
        print('     lons_per_step = ', self.lons_per_step.shape)
        print('     azimuths = ', self.azimuth_per_step.shape)
        print('     dist_per_step = ', self.dist_per_step.shape)

        self.shipparams_per_step.print_shape()

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

        print('Currently going from')
        print(self.start_temp)
        print('to')
        print(self.finish_temp)

    def define_variants(self):
        # branch out for multiple headings
        nof_input_routes = self.lats_per_step.shape[1]

        new_finish_one = np.repeat(self.finish_temp[0], nof_input_routes)
        new_finish_two = np.repeat(self.finish_temp[1], nof_input_routes)

        new_azi = geod.inverse(
            self.lats_per_step[0],
            self.lons_per_step[0],
            new_finish_one,
            new_finish_two
        )

        self.lats_per_step = np.repeat(self.lats_per_step, self.variant_segments + 1, axis=1)
        self.lons_per_step = np.repeat(self.lons_per_step, self.variant_segments + 1, axis=1)
        self.dist_per_step = np.repeat(self.dist_per_step, self.variant_segments + 1, axis=1)
        self.azimuth_per_step = np.repeat(self.azimuth_per_step, self.variant_segments + 1, axis=1)
        self.starttime_per_step = np.repeat(self.starttime_per_step, self.variant_segments + 1, axis=1)

        self.shipparams_per_step.define_variants(self.variant_segments)

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

        self.current_variant = new_azi['azi1']	# center courses around gcr
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
        #if(debug) : print('wind in move_boat_direct', wind)

        # get boat speed
        bs = boat.boat_speed_function(wind)

        ship_params = boat.get_fuel_per_time_netCDF(self.get_current_azimuth(), self.get_current_lats(),
                                                  self.get_current_lons(), self.time, wind)
        #ship_params.print()

        delta_time, delta_fuel, dist = self.get_delta_variables_netCDF(ship_params, bs)
        if (debug):
            print('delta_time: ', delta_time)
            print('delta_fuel: ', delta_fuel)
            print('dist: ', dist)
            print('is_last_step:', self.is_last_step)

        move = self.check_bearing(dist)

        if (debug):
            print('move:', move)

        if(self.is_last_step or self.is_pos_constraint_step):
            delta_time, delta_fuel, dist = self.get_delta_variables_netCDF_last_step(ship_params, bs)

        is_constrained = self.check_constraints(move, constraint_list)

        self.update_position(move, is_constrained, dist)
        self.update_time(delta_time)
        self.update_fuel(delta_fuel)
        self.update_shipparams(ship_params)
        self.count += 1

    def update_shipparams(self, ship_params_single_step):
        new_rpm=np.vstack((ship_params_single_step.get_rpm(), self.shipparams_per_step.get_rpm()))
        new_power=np.vstack((ship_params_single_step.get_power(), self.shipparams_per_step.get_power()))
        new_speed=np.vstack((ship_params_single_step.get_speed(), self.shipparams_per_step.get_speed()))

        self.shipparams_per_step.set_rpm(new_rpm)
        self.shipparams_per_step.set_power(new_power)
        self.shipparams_per_step.set_speed(new_speed)

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
