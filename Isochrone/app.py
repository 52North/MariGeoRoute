"""Flask main."""
import io
import logging
import datetime as dt
import os

from logging import FileHandler, Formatter
from flask import Flask, Response, render_template, request, send_from_directory
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import polars
import graphics
import weather
import router

# App Config.
app = Flask(__name__)
app.config.from_object('config')

state = {}
state['hour'] = 0


@app.route('/')
def hello():    #create dummy page here
    return 'Hello World!'

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


@app.route('/map')
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
    delta_time = 3600
    hours = 110

    vct_winds = weather.read_wind_vectors(windfile, model, hours, lat1, lon1, lat2, lon2)
    fct_winds = weather.read_wind_functions(model, hours)

    r_la1, r_lo1, r_la2, r_lo2 = app.config['DEFAULT_ROUTE']

    print('*************** SETTINGS *************')
    start = (r_la1, r_lo1)
    finish = (r_la2, r_lo2)
    print('start coordinates',start,finish)
    start_time = dt.datetime.strptime('2020111600', '%Y%m%d%H')
    print('start date', start_time)
    print('***************************************')


    boat = polars.boat_properties(boatfile)
    params = app.config

    iso3 = router.routing(
        start, finish,
        boat, fct_winds,
        start_time,
        delta_time, hours,
        params
    )

    fig = graphics.create_map(lat1, lon1, lat2, lon2, dpi)

    fig = graphics.plot_barbs(fig, vct_winds, 0)
    fig = graphics.plot_gcr(fig, r_la1, r_lo1, r_la2, r_lo2)
    fig = graphics.plot_isochrones(fig, iso3)

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
