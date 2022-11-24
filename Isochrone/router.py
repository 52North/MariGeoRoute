"""Routing functions."""
import utils
from IsoChrone import IsoChrone
from IsoFuel import IsoFuel
from RoutingAlgTimeFuelMin import RoutingAlgTimeFuelMin
from polars import Boat
from routeparams import RouteParams
from weather import WeatherCond

def modified_isochrone_routing(start, #r_la1, r_lo1
            finish, #r_la2, r_lo2
            boat : Boat,   #class containing boat polars, function
            wt : WeatherCond,  #dict containing wind functinos (model timestamp, vector of functions per hour)
            start_time,
            delta_time,
            steps,
            params,
            fig,
            verbose=False):
    """
    Do full isochrone routing.

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
    print('Modified isochrone routing...')
    ra=IsoChrone(start,finish,start_time, delta_time)
    ra.set_fig(fig)
    ra.set_steps(steps)
    ra.set_pruning_settings(params['ISOCHRONE_PRUNE_SECTOR_DEG_HALF'],params['ISOCHRONE_PRUNE_SEGMENTS'])
    ra.set_variant_segments(params['ROUTER_HDGS_SEGMENTS'], params ['ROUTER_HDGS_INCREMENTS_DEG'])
    min_time_route=ra.recursive_routing(boat, wt, verbose)

    #min_time_route.print_route()
    return min_time_route

def min_fuel_routing(
            start,  # r_la1, r_lo1
            finish,  # r_la2, r_lo2
            boat: Boat,  # class containing boat polars, function
            wt: WeatherCond,  # dict containing wind functinos (model timestamp, vector of functions per hour)
            start_time,
            delta_fuel,
            steps,
            params,
            fig,
            verbose=False):
    """
    Do full isochrone routing.

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

    ra_fuel=IsoFuel(start, finish, start_time, delta_fuel)
    ra_fuel.set_fig(fig)
    ra_fuel.set_steps(steps)
    ra_fuel.set_pruning_settings(params['ISOCHRONE_PRUNE_SECTOR_DEG_HALF'], params['ISOCHRONE_PRUNE_SEGMENTS'])
    ra_fuel.set_variant_segments(params['ROUTER_HDGS_SEGMENTS'], params['ROUTER_HDGS_INCREMENTS_DEG'])
    min_fuel_route = ra_fuel.recursive_routing(boat, wt, verbose)

    min_fuel_route['route'].print_route()
    return min_fuel_route

#
# def Squat(h, T, V_max, LWL, WWL, ukc, WVPI):
#     """Function for reducing the sailing velocity in deep water to the sailing velocity in shallow unconfined waters.
#     h:                              Array of the water depth in meters
#     V_max:                          Sailing velocity in deep water in meters per second
#     WWL:                            Width over Water Line of the vessel in meters
#     LWL:                            Length over Water Line of the vessel in meters
#     ukc:                            Minimal needed under keel clearance in  meters.
#     T:                              numpy array with the draft of the vessel. Numpy array has the shape of
#                                     the number of discretisations in the dynamic sailing velocity in meters
#     WVPI:                           total weight of the the vessel in tf
#     V:                              Array of sailing velocities reduced for squat, corresponding to the input arrat h.
#     """
#     Gamma_water = 1025
#     b = 9 * WWL
#     g = 9.81
#     ghv2 = g * h / (V_max ** 2)
#     squat_max = h - T - ukc
#     CB = WVPI / (LWL * WWL * T * Gamma_water)
#     AsAc = (WWL * T) / (b * h - WWL * T)
#     RH = (b * h - WWL * T) / (b + 2 * h + 2 * T + WWL)
#
#     VhV1 = (
#         1.002
#         + 0.005 * (np.sqrt(WWL * T) / RH)
#         - 0.1159 * (np.sqrt(WWL * T) / RH) ** 2
#         + 0.0191 * (np.sqrt(WWL * T) / RH) ** 3
#     )
#     V1Vinf = ((np.exp(ghv2) - np.exp(-ghv2)) / (np.exp(ghv2) + np.exp(-ghv2))) ** 0.5
#
#     V_grens = V_max * V1Vinf * VhV1
#     V_squat_max = np.zeros(len(h))
#     V = np.zeros(len(h))
#     for i in range(len(h)):
#         V_squat_max[i] = (
#             0
#             if squat_max[i] < 0
#             else (squat_max[i] * 30 / CB / (AsAc[i] ** (2 / 3))) ** (1 / 2.08)
#         )
#         V[i] = V_grens[i] if V_squat_max[i] > V_grens[i] else V_squat_max[i]
#
#     return V

