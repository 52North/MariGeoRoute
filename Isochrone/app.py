"""Flask main."""
import io
import logging
import graphics
from logging import FileHandler, Formatter
from flask import Flask, Response, render_template, request, send_from_directory
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import logging
import logging.handlers
import os
import warnings

import router
from polars import *
from weather import *
from Constraints import *

# App Config.
app = Flask(__name__)
app.config.from_object('config')

state = {}
state['hour'] = 0

'''
# Controllers.
@app.route('/', methods=["GET", "POST"])
def home():
    """Route handling."""

    if request.method == 'GET':
        return render_template(
            'pages/placeholder.home.html',
            hour=state['hour'])
    if request.method == 'POST':
        if 'increment' in request.form:
            state['hour'] = state['hour'] + 3
        elif 'decrement' in request.form:
            state['hour'] = state['hour'] - 3
        return render_template(
            'pages/placeholder.home.html',
            hour=state['hour'])


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/ico'),
                               'favicon.png', mimetype='image/vnd.microsoft.icon')

'''


@app.route('/')
def plot_map():
    ##
    # initialise logging
    logger = logging.getLogger('WRT')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(app.config['PERFORMANCE_LOG_FILE'], mode='w')
    fh.setLevel(logging.WARNING)
    fhinfo = logging.FileHandler(app.config['INFO_LOG_FILE'], mode='w')
    fhinfo.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    fh.setFormatter(formatter)
    fhinfo.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(fhinfo)

    ##
    # suppress warnings from mariPower
    warnings.filterwarnings("ignore")

    #graphics.merge_figs("/home/kdemmich/MariData/Code/Figures/NoDepthConstraint/", 5)
    #raise Exception('Stop here')

    """Route handling."""
    try:
        lat1 = request.args['lat1']
        lon1 = request.args['lon1']
        lat2 = request.args['lat2']
        lon2 = request.args['lon2']
    except (KeyError):
        lat1, lon1, lat2, lon2 = app.config['DEFAULT_MAP']
        dpi = app.config['DPI']
        logger.info('using default map coordinates')

    try:
        lat1 = float(lat1)
        lat2 = float(lat2)
        lon1 = float(lon1)
        lon2 = float(lon2)
    except (ValueError):
        raise ValueError('Expecting real values for map coordinates')

    # *******************************************
    # basic settings
    model = app.config['DEFAULT_GFS_MODEL']
    boatfile = app.config['DEFAULT_BOAT']
    windfile = app.config['DEFAULT_GFS_FILE']
    depthfile = app.config['DEFAULT_DEPTH_FILE']
    coursesfile = app.config['COURSES_FILE']
    figurepath = app.config['FIGURE_PATH']
    delta_time = app.config['DELTA_TIME_FORECAST']
    delta_fuel = app.config['DELTA_FUEL']
    hours = app.config['TIME_FORECAST']
    routing_steps = app.config['ROUTING_STEPS']
    lat1, lon1, lat2, lon2 = app.config['DEFAULT_MAP']
    r_la1, r_lo1, r_la2, r_lo2 = app.config['DEFAULT_ROUTE']
    start = (r_la1, r_lo1)
    finish = (r_la2, r_lo2)
    start_time = dt.datetime.strptime(app.config['DEFAULT_GFS_DATETIME'], '%Y%m%d%H')
    params = app.config

    # *******************************************
    # initialise boat
    boat = Tanker(-99)
    #boat.init_hydro_model_single_pars()
    #boat.init_hydro_model(windfile)
    boat.init_hydro_model_Route(windfile, coursesfile)
    boat.set_boat_speed(15)
    boat.calibrate_simple_fuel()
    #boat.write_simple_fuel()
    #boat.test_power_consumption_per_course()
    #boat.test_power_consumption_per_speed()

    #boat = SailingBoat(filepath=boatfile)

    # *******************************************
    # initialise weather
    wt = WeatherCondCMEMS(windfile, model, start_time, hours,3)
    wt.set_map_size(lat1, lon1, lat2, lon2)
    wt.add_depth_to_EnvData(depthfile)
    #wt = WeatherCondNCEP(windfile, model, start_time, hours, 3)
    #wt.check_ds_format()
    wt.init_wind_functions()
    wt.init_wind_vectors()
    #vct_winds = wt.read_wind_vectors(model, hours, lat1, lon1, lat2, lon2)


    # *******************************************
    # initialise constraints
    pars = ConstraintPars()
    land_crossing = LandCrossing()
    water_depth = WaterDepth(wt)
    water_depth.set_drought(20)
    #water_depth.plot_depth_map_from_file(depthfile, lat1, lon1, lat2, lon2)

    constraint_list = ConstraintsList(pars)
    constraint_list.add_neg_constraint(land_crossing)
    #constraint_list.add_neg_constraint(water_depth)
    constraint_list.print_settings()

    '''min_time_route = router.modified_isochrone_routing(
        start, finish,
        boat,
        wt,
        start_time,
        delta_time, routing_steps,
        params,
        fig
    )
    fig = min_time_route['fig']'''

    min_fuel_route = router.min_fuel_routing(
        start, finish,
        boat,
        wt,
        constraint_list,
        start_time,
        delta_fuel, routing_steps,
        params,
        figurepath
    )

    #boat.write_netCDF_courses(min_fuel_route['route'].azimuths_per_step, min_fuel_route['route'].lats_per_step, min_fuel_route['route'].lons_per_step, min_fuel_route['route'].starttime_per_step)

    #if not (min_fuel_route.__eq__(min_time_route)):
    #    raise ValueError('Routes not matching!')'''

    fig =  graphics.create_map(lat1, lon1, lat2, lon2, dpi)
    #fig = graphics.plot_route(fig, min_time_route['route'], graphics.get_colour(1))
    fig = graphics.plot_route(fig, min_fuel_route['route'], graphics.get_colour(1))
    fig = graphics.plot_legend(fig)

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)

    #plot route in constraints
    water_depth.plot_route_in_constraint(min_fuel_route['route'], graphics.get_colour(1), figurepath)

    return Response(output.getvalue(), mimetype='image/png')


# Error handlers.
@app.errorhandler(500)
def internal_error(error):
    """Error handling."""
    #return render_template('errors/500.html'), 500
    return 'Error 500'


@app.errorhandler(404)
def not_found_error(error):
    """Error handling."""
    #return render_template('errors/404.html'), 404
    return 'Error 404'


if not app.debug:
    file_handler = FileHandler('error.log')
    fmt = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    file_handler.setFormatter(Formatter(fmt))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# Default port:
if __name__ == '__main__':
    #app.run()
    app.run(host="localhost", port=5000, debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
