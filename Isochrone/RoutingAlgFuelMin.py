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
from isochrone import RoutingAlg
import utils

class RoutingAlgFuelMin(RoutingAlg):

    def __init__(self, route : RouteParams, time):
        RoutingAlg.__init__(self, route.start, route.finish, time)
        self.lats_per_step = route.lats_per_step
        self.lons_per_step = route.lons_per_step
        self.dist_per_step = route.dists_per_step
        self.full_dist_travelled = route.full_dist_travelled
        self.current_variant = route.rpm

        self.lats_per_step=np.tile(self.lats_per_step[:,np.newaxis],1)
        self.lons_per_step = np.tile(self.lons_per_step[:, np.newaxis], 1)
        self.dist_per_step = np.tile(self.dist_per_step[:, np.newaxis], 1)

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
