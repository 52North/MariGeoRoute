import os

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# DPI properties
DPI = 96

# Secret key for session management. You can generate random strings here:
# https://randomkeygen.com/
# SECRET_KEY = 'my precious'

# Defaults - self-explanatory
DEFAULT_MAP = [53, 11,60,22] #Rügen to Gotland: [53, 11,60,23]  [54.87, 13.33, 58.28, 16.97]
#DEFAULT_MAP = [53, 12,60,19.5] #Rügen to Gotland: [53, 11,60,23]  [54.87, 13.33, 58.28, 16.97]
DEFAULT_ROUTE =  [54.87, 13.33, 58.28, 17.06]   #plotting of isochrone approach [54.87, 13.33, 55.73, 16.96] #test last step functionality: [54.87, 13.33, 54.9, 13.46]  # Rügen to Gotland: [54.87, 13.33, 58.57, 19.78]  #english channel: [50.3, 0, 51.90, 3.92], mediteranen sea: [43.5,7.2, 33.8,35.5], kiel canal: [53, 7, 55, 12]
TIME_FORECAST = 20     # [hours]
ROUTING_STEPS = 10
DELTA_TIME_FORECAST = 3600 # [seconds]
#DELTA_FUEL = 30000000*1000*1 # [Ws]
DELTA_FUEL = 1*1000 # [kg]
#DEFAULT_GFS_DATETIME = '2020111600' #NCEP
#DEFAULT_GFS_DATETIME = '202302007' #CMEMS
DEFAULT_GFS_DATETIME = '2023021012' #CMEMS
DEFAULT_GFS_HOUR = '06'
DEFAULT_GFS_FCST = '000'
DEFAULT_GFS_RESOLUTION = '1p00'
#DEFAULT_GFS_FILE = '/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/Data/2019122212/20205150000_split13.grb'
#DEFAULT_GFS_FILE = '/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/Data/2019122212/2019122212f000'
#DEFAULT_GFS_FILE = '/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/Data/2019122212/20205150000_split13.nc'                #NCEP
#DEFAULT_GFS_FILE = '/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/Data/20221110/38908a16-7a3c-11ed-b628-0242ac120003.nc'  #CMEMS needs lat: 30 to 45, lon: 0 to 20
#DEFAULT_GFS_FILE = '/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/Data/20221110/77175d34-9006-11ed-b628-0242ac120003_Brighton_Rotterdam.nc'

#DEFAULT_GFS_FILE = '/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/Data/20221110/202102_02-10_Halmsstadt_to_Gotland.nc'
DEFAULT_GFS_FILE = '/home/kdemmich/Downloads/9a0c767e-abb5-11ed-b8e3-e3ae8824c4e4.nc'

#DEFAULT_DEPTH_FILE = '/home/kdemmich/Downloads/ETOPO_2022_v1_30s_N90W180_bed.nc'
DEFAULT_DEPTH_FILE = '/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/ETOPO_2022_v1_30s_N90W180_bed.nc'
PERFORMANCE_LOG_FILE = '/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/log/performance_warnings.log'
INFO_LOG_FILE = '/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/log/info.log'
FIGURE_PATH='/home/kdemmich/MariData/Code/Figures'
COURSES_FILE = '/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/CoursesRoute.nc'
DEFAULT_GFS_MODEL = '2021020407'

# Isochrone routing parameters
ROUTER_HDGS_SEGMENTS =  30 #6            #total number of headings : put even number!!   #30
ROUTER_HDGS_INCREMENTS_DEG = 6 #30         #increment of headings
ROUTER_RPM_SEGMENTS = 1
ROUTER_RPM_INCREMENTS_DEG = 1
ISOCHRONE_EXPECTED_SPEED_KTS = 8
ISOCHRONE_PRUNE_SECTOR_DEG_HALF = 91    #angular range of azimuth that is considered for pruning (only one half)
ISOCHRONE_PRUNE_SEGMENTS = 20#36          #total number of azimuth bins that are used for pruning in prune sector which is 2x ISOCHRONE_PRUNE_SECTOR_DEG_HALF : put even number ! #3

# boat settings
DEFAULT_BOAT = '/home/kdemmich/MariData/Code/MariGeoRoute/Isochrone/Data/polar-ITA70.csv'  #contains some boat specifics
