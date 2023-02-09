from routeparams import RouteParams
from Constraints import *
from weather import WeatherCondCMEMS
import graphics
import config

if __name__ == "__main__":
    filename1 = "/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/min_time_routeroute.json"
    filename2 = "/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/depth.json"
    figurefile = "/home/kdemmich/MariData/Code/Figures"
    rp_read1 = RouteParams.from_file(filename1)
    rp_read2 = RouteParams.from_file(filename2)

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
    # plotting routes
    fig, ax = plt.subplots(figsize=(12, 7))
    fig, ax = water_depth.plot_constraint(fig, ax)
    #water_depth.plot_route_in_constraint(rp_read, 0, fig, ax)
    rp_read1.plot_route(ax, graphics.get_colour(0), "route 1")
    rp_read2.plot_route(ax, graphics.get_colour(1), "route 2")
    ax.legend()
    plt.savefig(figurefile + '/route_waterdepth.png')

    ##
    # plotting power vs. distance
    fig, ax = plt.subplots(figsize=(12, 8), dpi=96)
    rp_read1.plot_power_vs_dist(graphics.get_colour(0), "route 1")
    rp_read2.plot_power_vs_dist(graphics.get_colour(1), "route 2")
    ax.legend()
    plt.savefig(figurefile + '/route_power.png')






