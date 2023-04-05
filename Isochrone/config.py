import os
from dotenv import load_dotenv

load_dotenv()

##
# Defaults
DEFAULT_MAP = [53, 11,60,22] #Rügen to Gotland: [53, 11,60,23]  [54.87, 13.33, 58.28, 16.97]
#DEFAULT_MAP = [53, 12,60,19.5] #Rügen to Gotland: [53, 11,60,23]  [54.87, 13.33, 58.28, 16.97]
DEFAULT_ROUTE =[54.87, 13.33, 58.28, 17.06]   #plotting of isochrone approach [54.87, 13.33, 55.73, 16.96] #test last step functionality: [54.87, 13.33, 54.9, 13.46]  # Rügen to Gotland: [54.87, 13.33, 58.57, 19.78]  #english channel: [50.3, 0, 51.90, 3.92], mediteranen sea: [43.5,7.2, 33.8,35.5], kiel canal: [53, 7, 55, 12]
TIME_FORECAST = 20              # forecast hours weather
ROUTING_STEPS = 11               # number of routing steps
DELTA_TIME_FORECAST = 3600      # time resolution of weather forecast (seconds)
#DELTA_FUEL = 30000000*1000*1 # [Ws]
DELTA_FUEL = 1*1000             # amount of fuel per routing step (kg)
START_TIME = '2023021012'       # start time of travelling
BOAT_SPEED = 15                 # (m/s)
BOAT_DROUGHT = 10                 # (m)

##
# File paths
WEATHER_DATA = os.environ['WEATHER_DATA']   # path to weather data
DEPTH_DATA = os.environ['DEPTH_DATA']       # path to depth data
PERFORMANCE_LOG_FILE = os.environ['PERFORMANCE_LOG_FILE']   # path to log file which logs performance
INFO_LOG_FILE = os.environ['INFO_LOG_FILE'] # path to log file which logs information
FIGURE_PATH = os.environ['FIGURE_PATH']     # path to figure repository
COURSES_FILE = os.environ['BASE_PATH'] + '/CoursesRoute.nc'     # path to file that acts as intermediate storage for courses per routing step
ROUTE_PATH = os.environ['ROUTE_PATH']

##
# Isochrone routing parameters
ROUTER_HDGS_SEGMENTS =  30               # total number of courses : put even number!!
ROUTER_HDGS_INCREMENTS_DEG = 6           # increment of headings
ROUTER_RPM_SEGMENTS = 1                  # not used yet
ROUTER_RPM_INCREMENTS_DEG = 1            # not used yet
ISOCHRONE_EXPECTED_SPEED_KTS = 8
ISOCHRONE_PRUNE_SECTOR_DEG_HALF = 91     # angular range of azimuth angle that is considered for pruning (only one half)
ISOCHRONE_PRUNE_SEGMENTS = 20            # total number of azimuth bins that are used for pruning in prune sector which is 2x ISOCHRONE_PRUNE_SECTOR_DEG_HALF : put even number !

##
# boat settings
DEFAULT_BOAT = os.environ['BOAT_FILE']   # path to data for sailing boat (not maintained)

