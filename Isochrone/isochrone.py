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
    ncount: int # total number of routing steps
    count: int  # current routing step
    start: tuple  # lat, lon at start
    finish: tuple  # lat, lon at end
    gcr_azi: float  # azimut of great circle route
    lats_per_step: np.ndarray  # lats: (M,N) array, N=headings+1, M=steps (M decreasing)
    lons_per_step: np.ndarray  # longs: (M,N) array, N=headings+1, M=steps
    variant: np.ndarray  # azimuth: (M,N) array, N=headings+1, M=steps
    dist_per_step: np.ndarray  # geodesic distance traveled per time stamp: (M,N) array, N=headings+1, M=steps
    last_azimuth: np.ndarray  # current azimuth
    full_dist_travelled: np.ndarray  # full geodesic distance since start
    time: dt.datetime  # current datetime
    full_time_travelled: dt.timedelta  # time elapsed since start

    variant_segments: int       # number of variant segments in the range of -180° to 180°
    variant_increments_deg: int
    expected_speed_kts: int
    prune_sector_deg_half: int  # angular range of azimuth that is considered for pruning (only one half)
    prune_segments: int    # number of azimuth bins that are used for pruning

    def __init__(self, start, finish, time):
        self.count = 0
        self.start = start
        self.finish = finish
        self.lats_per_step = np.array([[start[0]]])
        self.lons_per_step = np.array([[start[1]]])
        self.variants = np.array([[None]])
        self.dist_per_step = np.array([[0]])
        self.full_dist_travelled = np.array([])
        self.time = time
        self.full_time_traveled = dt.timedelta(seconds=0)

        gcr = self.calculate_gcr(start, finish)
        self.last_azimuth = gcr
        self.gcr_azi = gcr

        ut.print_line()
        print('Initialising routing: ' + str(start) + ' to ' + str(finish))
        print('     route from ' + str(start) + ' to ' + str(finish))
        print('     start time ' + str(time))

    def set_steps(self, steps):
        self.ncount=steps

    def set_variant_segments(self,segments):
        self.variant_segments=segments

    def set_pruning_settings(self, sector_deg_half, seg):
        self.prune_sector_deg_half=sector_deg_half
        self.prune_segments=seg

    def set_variant_segments(self, seg, inc):
        self.variant_segments = seg
        self.variant_increments_deg = inc

    def calculate_gcr(self, start, finish):
        gcr = geod.inverse([start[0]], [start[1]], [finish[0]], [
            finish[1]])  # calculate distance between start and end according to Vincents approach, return dictionary
        return gcr['azi1']

    def print_current_step(self):
        print('step = ', self.count)
        print('lats_per_step = ', self.lats_per_step)
        print('lons_per_step = ', self.lons_per_step)
        print('variants = ', self.variants)
        print('dist_per_step = ', self.dist_per_step)
        print('full_dist_travelled = ', self.full_dist_travelled)
        print('time = ', self.time)
        print('full_time_traveled = ', self.full_time_traveled)

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
        for i in range(self.ncount):
            utils.print_line()
            print('Step ', i)

            vars = self.define_variants()
            gcrs = self.move_boat_direct(winds, vars, boat, delta_time)
            self.pruning(gcrs['azi1'], gcrs['s12'], True)

            #self.print_current_step()
            self.count+=1

        route = self.terminate()
        return route

    def define_variants(self):
        # branch out for multiple headings
        nof_routes = self.lats_per_step.shape[1]

        self.lats_per_step = np.repeat(self.lats_per_step, self.variant_segments + 1, axis=1)
        self.lons_per_step = np.repeat(self.lons_per_step, self.variant_segments + 1, axis=1)
        self.variants = np.repeat(self.variants, self.variant_segments + 1, axis=1)
        self.dist_per_step = np.repeat(self.dist_per_step, self.variant_segments + 1, axis=1)

        if(not ((self.lats_per_step.shape[1]==self.lons_per_step.shape[1]) and
            (self.lats_per_step.shape[1]==self.variants.shape[1]) and
            (self.lats_per_step.shape[1]==self.dist_per_step.shape[1]))):
            raise 'define_variants: number of columns not matching!'

        if(not ((self.lats_per_step.shape[0]==self.lons_per_step.shape[0]) and
            (self.lats_per_step.shape[0]==self.variants.shape[0]) and
            (self.lats_per_step.shape[0]==self.dist_per_step.shape[0]) and
            (self.lats_per_step.shape[0]==(self.count+1)))):
            raise ValueError('define_variants: number of rows not matching! count = ' + str(self.count) + ' lats per step ' + str(self.lats_per_step.shape[0]))

        # determine new headings - centered around gcrs X0 -> X_prev_step
        hdgs = self.last_azimuth
        delta_hdgs = np.linspace(
            -self.variant_segments * self.variant_increments_deg,
            +self.variant_segments * self.variant_increments_deg,
            self.variant_segments + 1)
        delta_hdgs = np.tile(delta_hdgs, nof_routes)
        hdgs = np.repeat(hdgs, self.variant_segments + 1)

        hdgs = hdgs - delta_hdgs

        return hdgs

    def move_boat_direct(self, winds, hdgs, boat: Boat, delta_time):
        """
                calculate new boat position for current time step based on wind and boat function
            """
        current_lats = self.lats_per_step[0, :]
        current_lons = self.lons_per_step[0, :]
        start_lats = np.repeat(self.start[0], self.lats_per_step.shape[1])
        start_lons = np.repeat(self.start[1], self.lons_per_step.shape[1])

        #get wind speed (tws) and angle (twa)
        winds = wind_function(winds, (current_lats, current_lons), self.time)
        twa = winds['twa']
        tws = winds['tws']
        wind = {'tws': tws, 'twa': twa - hdgs}

        #get boat speed
        bs = boat.boat_speed_function(wind)

        # update boat position
        dist = delta_time * bs
        move = geod.direct(current_lats, current_lons, hdgs, dist)

        self.lats_per_step = np.vstack((move['lat2'], self.lats_per_step))
        self.lons_per_step = np.vstack((move['lon2'], self.lons_per_step))
        self.variants = np.vstack((hdgs, self.variants))
        self.dist_per_step = np.vstack((dist, self.dist_per_step))

        # determine gcrs from start to new isochrone
        gcrs = geod.inverse(start_lats, start_lons, move['lat2'], move['lon2'])
        self.full_dist_travelled=gcrs['s12']
        self.last_azimuth=gcrs['azi1']

        # remove those which ended on land
        is_on_land = globe.is_land(move['lat2'], move['lon2'])
        gcrs['s12'][is_on_land] = 0  # to check
        # for i in range(int((x2 - x1) / STEP) + 1): #62.3, 17.6, 59.5, 24.6
        #     try:
        #         x = x1 + i * STEP
        #         y = (y1 - y2) / (x1 - x2) * (x - x1) + y1
        #     except:
        #         continue
        #     is_on_land = globe.is_land(float(x), float(y))
        #     print(is_on_land)
        #     # if not is_on_land:
        #     # print("in water")
        #
        #     if is_on_land:
        #         # print("crosses land")
        #
        #         return True

        # print('isonland',is_on_land)
        # z = globe.is_land(lats, lons)
        # print('value of z',type(z))
        # if z=='True':
        #     is_on_land = globe.is_land(move['lats2'], move['lons2'])
        #     print(is_on_land)

        return gcrs

    def pruning(self,  x, y, trim=True):
        """
              generate view of the iso that only contains the longests route per azimuth segment

              Binned statistic.
              +            iso2 = prune_isochrone(iso2, 'azi02', 's02', bins, True)
              print('iso2 ',iso2)  #

                    Parameters:
                    iso: isochrone dictionary
                    x: values to binarize
                    y: values to apply max to
                    bins: bins edges, dimension is n_bins + 1
                    trim: whether return just one of max values
                    Returns:
                        pruned isochrone dictionary with max values in each bin
                   """

        mean_dist = np.mean(self.full_dist_travelled)
        gcr_point = geod.direct(
            [self.start[0]],
            [self.start[1]],
            self.gcr_azi, mean_dist)

        new_azi = geod.inverse(
            gcr_point['lat2'],
            gcr_point['lon2'],
            [self.finish[0]],
            [self.finish[1]]
        )

        azi0s = np.repeat(
            new_azi['azi1'],
            self.prune_segments + 1)

        # determine bins
        delta_hdgs = np.linspace(
            -self.prune_sector_deg_half,
            +self.prune_sector_deg_half,
            self.prune_segments + 1)  # -90,+90,181

        bins = azi0s - delta_hdgs
        bins = np.sort(bins)

        idxs = []
        bin_stat, bin_edges, bin_number = binned_statistic(
            self.last_azimuth, self.full_dist_travelled, statistic=np.nanmax, bins=bins)

        if trim:
            for i in range(len(bin_edges) - 1):
                try:
                    idxs.append(
                        np.where(self.full_dist_travelled == bin_stat[i])[0][0])
                except IndexError:
                    pass
            idxs = list(set(idxs))
        else:
            for i in range(len(bin_edges) - 1):
                idxs.append(np.where(self.full_dist_travelled == bin_stat[i])[0])
            idxs = list(set([item for subl in idxs for item in subl]))


        # Return a trimmed isochrone
        lats_new = self.lats_per_step[:, idxs]
        lons_new = self.lons_per_step[:, idxs]
        var_new = self.variants[:, idxs]
        dist_new = self.dist_per_step[:, idxs]
        curr_azi_new = self.last_azimuth[idxs]
        full_dist_new = self.full_dist_travelled[idxs]

        self.lats_per_step = lats_new
        self.lons_per_step = lons_new
        self.variants = var_new
        self.dist_per_step = dist_new
        self.last_azimuth = curr_azi_new
        self.full_dist_travelled = full_dist_new

        #print('last_azimuth', self.last_azimuth)
        #print('inx', idxs)

        # print("rpm = ",boat.get_rpm())
        # print("Used fuel", boat.get_fuel_per_time(delta_time))

    def terminate(self):
        idx = np.argmax(self.full_dist_travelled)

        route = RouteParams(
            count = self.count,  # routing step
            start = self.start,  # lat, lon at start
            finish = self.finish,  # lat, lon at end
            fuel = -999.,  # sum of fuel consumption [t]
            rpm = -999.,  # propeller [revolutions per minute]
            route_type = 'min_time_route',  # route name
            time = self.time,  # time needed for the route [seconds]
            lats_per_step=self.lats_per_step[:, idx],
            lons_per_step=self.lons_per_step[:, idx],
            azimuths_per_step=self.variants[:, idx],
            dists_per_step=self.dist_per_step[:, idx],
            full_dist_travelled=self.full_dist_travelled[idx]
        )
        #route.print_route()

        return route
