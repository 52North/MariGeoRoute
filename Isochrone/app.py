"""Flask main."""
import io
import logging
import datetime as dt
import os

from logging import FileHandler, Formatter
from flask import Flask, Response, render_template, request, send_from_directory
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from polars import Boat
from weather import WeatherCond, WeatherCondNCEP, WeatherCondCMEMS
from routeparams import RouteParams

import graphics
import weather
import router
import utils as ut

# App Config.
app = Flask(__name__)
app.config.from_object('config')

state = {}
state['hour'] = 0


#@app.route('/')
#def hello():  #create dummy page here
#    return 'Hello World!'

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
    """Route handling."""
    try:
        lat1 = request.args['lat1']
        lon1 = request.args['lon1']
        lat2 = request.args['lat2']
        lon2 = request.args['lon2']
    except (KeyError):
        lat1, lon1, lat2, lon2 = app.config['DEFAULT_MAP']
        dpi = app.config['DPI']
        logging.log(logging.WARNING, 'using default coordinates')

    try:
        lat1 = float(lat1)
        lat2 = float(lat2)
        lon1 = float(lon1)
        lon2 = float(lon2)
    except (ValueError):
        logging.log(logging.ERROR, 'expecting real values')

    # fig = graphics.create_maps(lat1, lon1, lat2, lon2, dpi, 4)

    # try:
    #     latest = request.args['latest']
    # except KeyError:
    #     latest = False
    # if latest:
    #     weather_file = download_latest_gfs(0)
    # else:
    #     weather_file = app.config['DEFAULT_GFS_FILE']

    # try:
    #     hour = request.args['hour']
    # except (KeyError):
    #     hour = 0

    model = app.config['DEFAULT_GFS_MODEL']
    boatfile = app.config['DEFAULT_BOAT']
    windfile = app.config['DEFAULT_GFS_FILE']
    delta_time = app.config['DELTA_TIME_FORECAST']
    hours = app.config['TIME_FORECAST']
    lat1, lon1, lat2, lon2 = app.config['DEFAULT_MAP']


    r_la1, r_lo1, r_la2, r_lo2 = app.config['DEFAULT_ROUTE']
    start = (r_la1, r_lo1)
    finish = (r_la2, r_lo2)
    start_time = dt.datetime.strptime(app.config['DEFAULT_GFS_DATETIME'], '%Y%m%d%H')

    boat = Boat(rpm=-99, filepath=boatfile)
    boat.set_rpm(60)
    params = app.config

    wt = WeatherCondCMEMS(windfile, model, start_time, hours,3)
    #wt.check_ds_format()
    wt.set_map_size(lat1, lon1, lat2, lon2)
    wt.init_wind_functions()
    vct_winds = wt.read_wind_vectors(model, hours, lat1, lon1, lat2, lon2)

    min_time_route = router.modified_isochrone_routing(
        start, finish,
        boat,
        wt,
        start_time,
        delta_time, hours,
        params)


    '''min_fuel_route = router.min_fuel_routing(
        min_time_route,
        boat,
        fct_winds,
        start_time,
        delta_time,
        params
    )

    if not (min_fuel_route.__eq__(min_time_route)):
        raise ValueError('Routes not matching!')'''

    fig = graphics.create_map(lat1, lon1, lat2, lon2, dpi)

    fig = graphics.plot_barbs(fig, vct_winds, 0)
    fig = graphics.plot_gcr(fig, r_la1, r_lo1, r_la2, r_lo2)
    fig = graphics.plot_route(fig, min_time_route, graphics.get_colour(1))
    #fig = graphics.plot_route(fig, min_fuel_route, graphics.get_colour(1))
    fig = graphics.plot_legend(fig)

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)

    # Write the file as well
    with open('/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/Data/Screenshots/map8.png', 'wb') as f:
        f.write(output.getbuffer())

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
