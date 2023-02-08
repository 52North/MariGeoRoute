from routeparams import RouteParams
from Constraints import *
from weather import WeatherCondCMEMS
import config

if __name__ == "__main__":
    filename = "/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/min_time_routeroute.json"
    figurefile = "/home/kdemmich/MariData/Code/Figures"
    rp_read = RouteParams.from_file(filename)
    rp_read.print_route()

    ##
    # init wheather
    windfile = config.DEFAULT_GFS_FILE
    model = config.DEFAULT_GFS_MODEL
    start_time = dt.datetime.strptime(config.DEFAULT_GFS_DATETIME, '%Y%m%d%H')
    hours = config.TIME_FORECAST
    lat1, lon1, lat2, lon2 = config.DEFAULT_MAP
    depthfile = config.DEFAULT_DEPTH_FILE
    wt = WeatherCondCMEMS(windfile, model, start_time, hours, 3)
    wt.set_map_size(lat1, lon1, lat2, lon2)
    wt.add_depth_to_EnvData(depthfile)

    ##
    # init Constraints
    water_depth = WaterDepth(wt)
    water_depth.set_drought(20)

    ##
    # plotting
    water_depth.plot_route_in_constraint(rp_read, 0, figurefile)

