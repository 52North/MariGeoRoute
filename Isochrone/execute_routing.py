import io
import logging
import os
import warnings
import logging.handlers
from logging import FileHandler, Formatter

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import config
import utils.graphics as graphics
from ship.ship import *
from weather import *
from constraints.constraints import *
from algorithms.routingalg_factory import *

def merge_figures_to_gif(path, nof_figures):
    graphics.merge_figs(path, nof_figures)

if __name__ == "__main__":
    ##
    # initialise logging
    logger = logging.getLogger('WRT')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(config.PERFORMANCE_LOG_FILE, mode='w')
    fh.setLevel(logging.WARNING)
    fhinfo = logging.FileHandler(config.INFO_LOG_FILE, mode='w')
    fhinfo.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    fh.setFormatter(formatter)
    fhinfo.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(fhinfo)

    ##
    # suppress warnings from mariPower
    warnings.filterwarnings("ignore")

    # *******************************************
    # basic settings
    model = config.START_TIME
    boatfile = config.DEFAULT_BOAT
    windfile = config.WEATHER_DATA
    depthfile = config.DEPTH_DATA
    coursesfile = config.COURSES_FILE
    figurepath = config.FIGURE_PATH
    routepath = config.ROUTE_PATH
    delta_time = config.DELTA_TIME_FORECAST
    delta_fuel = config.DELTA_FUEL
    hours = config.TIME_FORECAST
    routing_steps = config.ROUTING_STEPS
    lat1, lon1, lat2, lon2 = config.DEFAULT_MAP
    r_la1, r_lo1, r_la2, r_lo2 = config.DEFAULT_ROUTE
    start = (r_la1, r_lo1)
    finish = (r_la2, r_lo2)
    start_time = dt.datetime.strptime(config.START_TIME, '%Y%m%d%H')

    # *******************************************
    # initialise boat
    boat = Tanker(-99)
    # boat.init_hydro_model_single_pars()
    # boat.init_hydro_model(windfile)
    boat.init_hydro_model_Route(windfile, coursesfile)
    boat.set_boat_speed(config.BOAT_SPEED)
    # boat.calibrate_simple_fuel()
    # boat.write_simple_fuel()
    # boat.test_power_consumption_per_course()
    # boat.test_power_consumption_per_speed()

    # boat = SailingBoat(filepath=boatfile)

    # *******************************************
    # initialise weather
    wt = WeatherCondCMEMS(windfile, model, start_time, hours, 3)
    wt.set_map_size(lat1, lon1, lat2, lon2)
    #wt.add_depth_to_EnvData(depthfile)
    # wt = WeatherCondNCEP(windfile, model, start_time, hours, 3)
    # wt.check_ds_format()
    wt.init_wind_functions()
    wt.init_wind_vectors()
    # vct_winds = wt.read_wind_vectors(model, hours, lat1, lon1, lat2, lon2)

    # *******************************************
    # initialise constraints
    pars = ConstraintPars()
    land_crossing = LandCrossing()
    water_depth = WaterDepth(wt)
    water_depth.set_drought(config.BOAT_DROUGHT)
    # water_depth.plot_depth_map_from_file(depthfile, lat1, lon1, lat2, lon2)
    on_map = StayOnMap()
    on_map.set_map(lat1, lon1, lat2, lon2)
    #over_waypoint = PositiveConstraintPoint(55.796111, 3.100278)   #Route 1, good weather
    #over_waypoint = PositiveConstraintPoint(54.608889, 6.179722)    #Route 1, ok weather
    #over_waypoint = PositiveConstraintPoint(55.048333, 5.130000)    #Route 1, ok weather
    #over_waypoint = PositiveConstraintPoint(45.715000, -5.502222)    #Route 2, good weather
    #over_waypoint = PositiveConstraintPoint(41.70, 3.96)  # Route 2, good weather
    #over_waypoint1 = PositiveConstraintPoint(36.03, -5.21)
    #over_waypoint2 = PositiveConstraintPoint(35.96, -5.53)    #Route 2, good weather
    #over_waypoint = PositiveConstraintPoint(38.78, -9.63)
    over_waypoint  = PositiveConstraintPoint(48.67, -5.28)
    over_waypoint1 = PositiveConstraintPoint(47, -5.55)
    over_waypoint2 = PositiveConstraintPoint(46.97, -5.55)
    #over_waypoint2 = PositiveConstraintPoint(46.5, -5.55)
    over_waypoint3 = PositiveConstraintPoint(45.715000, -5.502222)

    constraint_list = ConstraintsList(pars)
    constraint_list.add_neg_constraint(land_crossing)
    constraint_list.add_neg_constraint(on_map)
    #constraint_list.add_neg_constraint(water_depth)
    constraint_list.add_pos_constraint(over_waypoint)
    constraint_list.add_pos_constraint(over_waypoint1)
    constraint_list.add_pos_constraint(over_waypoint2)
    constraint_list.add_pos_constraint(over_waypoint3)
    #constraint_list.add_pos_constraint(over_waypoint1)
    #constraint_list.add_pos_constraint(over_waypoint2)
    constraint_list.print_settings()

    # *******************************************
    # initialise rout
    route_factory = RoutingAlgFactory()
    min_fuel_route = route_factory.get_routing_alg('ISOFUEL')
    #min_fuel_route.init_fig(wt)

    # *******************************************
    # routing
    min_fuel_route = min_fuel_route.recursive_routing(boat, wt, constraint_list)
    min_fuel_route.print_route()
    min_fuel_route.write_to_file(str(min_fuel_route.route_type) + "route.json")
    min_fuel_route.return_route_to_API(routepath + str(min_fuel_route.route_type) + "route.json")

    # *******************************************
    # plot route in constraints
    fig, ax = plt.subplots(figsize=(12, 7))
    water_depth.plot_route_in_constraint(min_fuel_route, graphics.get_colour(1), fig, ax)
    plt.savefig(figurepath + '/route_waterdepth.png')
