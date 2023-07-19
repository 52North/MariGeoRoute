import glob
import os
import zipfile
#from dotenv import load_dotenv
import psycopg2
import requests
import geopandas as gpd
from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy import inspect
import logging


# Configure the logger
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')

# Create a logger instance
logger = logging.getLogger(__name__)

# load_dotenv()

# Retrieve the metadata from the Geofabrik portal
response = requests.get('https://download.geofabrik.de/index-v1-nogeom.json')
metadata = response.json()
features = metadata['features']

# Print the URLs for the first 25 dataset files
for feature in features[:25]:
    urls = feature['properties']['urls']
    # print(urls['pbf'])

# Print the URLs for European countries
#print('\nChecking the list of the dataset url for european countries\n')
european_urls = []
for feature in features:
    properties = feature['properties']
    urls = properties['urls']
    if (urls['pbf'].split('/')[3] == 'europe' and
        len(urls['pbf'].split('/')) == 5 and
            properties['id'] not in ('dach', 'alps', 'britain-and-ireland')):
        european_urls.append(urls['pbf'])
        # print(urls['pbf'])


# Download the European country dataset files
def download_files(urls):
    for i, url in enumerate(urls[:2], start=1):
        print(f'Downloading file {i}...')
        local_filename = url.split('/')[-1]
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)



# Check if osmosis exist amd install if do not exist
osmosis_path = "/osmosis/bin/osmosis"
if not os.path.exists(osmosis_path):
    # Install osmosis
    os.makedirs("/osmosis/bin/", exist_ok=True)
    osmosis_url = "https://github.com/openstreetmap/osmosis/releases/download/0.48.3/osmosis-0.48.3.zip"
    response = requests.get(osmosis_url)
    with open("osmosis.zip", "wb") as f:
        f.write(response.content)
    with zipfile.ZipFile("osmosis.zip", "r") as zip_ref:
        zip_ref.extractall("/osmosis/")
    os.remove("osmosis.zip")


# Get the current directory
dir_path = os.getcwd()

# Create empty list to hold file paths
seamarks_list = []

# Loop through all files in directory
for file in os.listdir(dir_path):
    # Check if file is a .pbf file
    if file.endswith(".pbf"):
        # If file is a .pbf file, append its path to the file_list
        seamarks_list.append(os.path.join(dir_path, file))

# Replace backlash by forward slash
seamarks_list1 = [p.replace("\\", "/") for p in seamarks_list]
print(seamarks_list1)


def check_for_schema():
    # print(os.environ("POSTGIS_PASSWORD"))
    conn = psycopg2.connect(
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host='db',
        port='5432'
    )
    cur = conn.cursor()
# Run SQL query to create the hstore extension
    cur.execute("CREATE EXTENSION IF NOT EXISTS hstore;")
    conn.commit()


    sql_files = glob.glob("/osmosis/script/*pgsnapshot_schema_0.6*.sql")
    desired_substrings = ['pgsnapshot_schema_0.6.sql',
                          'pgsnapshot_schema_0.6_action.sql', 'pgsnapshot_schema_0.6_linestring.sql']

    desired_files = [s for s in sql_files if s.endswith(
        tuple(desired_substrings))]

    for file_path in desired_files:
        with open(file_path, "r") as file:
            sql_query = file.read()
        cur = conn.cursor()
        # print(sql_query)
        cur.execute(sql_query)
        conn.commit()


def read_pbf_files(seamark_list2):
    # Loop through the list of seamarks files
    for smk in seamark_list2:
        # Extract Seamarks from the OSM data using Osmosis
        pbf = smk
        filter_tag = 'accept-nodes'
        filter_tag_way = 'reject-ways'
        seamark = 'seamark:type=*'
        xml = smk[:-4]
        db = os.environ["POSTGRES_DB"]
        user = os.environ["POSTGRES_USER"]
        password = os.environ["POSTGRES_PASSWORD"]

        cmd = f'{osmosis_path} --read-pbf {pbf} --tag-filter {filter_tag_way} --tag-filter {filter_tag} {seamark}  --tag-filter accept-relations --write-pgsql  host="db" database={db} user={user} password={password} validateSchemaVersion=no'
        print(cmd)
        os.system(cmd)


def download_world_seamarks():
    seamarks_world_url = "http://tiles.openseamap.org/seamark/world.osm"

    response = requests.get(seamarks_world_url)

    with open("/tmp/data.osm", "wb") as f:
        print(f'Downloading file {seamarks_world_url} started.....')
        f.write(response.content)
        print(f'Downloading file {seamarks_world_url} completed')


def read_xml_files(filenames):

    for filename in filenames:
        xml = filename
        filter_tags = ['accept-nodes', 'accept-ways', 'accept-relations']
        tag = 'seamark:type=*'
        tf = '--tag-filter'
        db = os.environ["POSTGRES_DB"]
        user = os.environ["POSTGRES_USER"]
        password = os.environ["POSTGRES_PASSWORD"]

        cmd = f'{osmosis_path} --read-xml {xml} {tf} {filter_tags[0]} {tf} {filter_tags[1]} {tf} {filter_tags[2]} {tag} --write-pgsql  host="db" database={db} user={user} password={password} validateSchemaVersion=no'
        print(cmd)
        os.system(cmd)


def save_shp_coastlines_water():

    logger.info("saving shapefiles of land polygons and water polygons")

    # Set up the database connection
    engine = create_engine(
        f'postgresql://{os.environ["POSTGRES_USER"]}:{os.environ["POSTGRES_PASSWORD"]}@db:5432/mydatabase')

    # Create an inspector object for the engine
    inspector = inspect(engine)

    #inspector = Inspector.from_engine(engine)

    # Define the URL to download the data from
    coast_url = 'https://osmdata.openstreetmap.de/download/water-polygons-split-4326.zip'
    land_url = 'https://osmdata.openstreetmap.de/download/land-polygons-complete-4326.zip'

    url = [coast_url, land_url]
    name = ['water_polygons', 'land_polygons']
    folder = ['water-polygons-split-4326', 'land-polygons-complete-4326']

    for x, y, z in zip(name, url, folder):
        # Check if the unzipped directory already exists in the current directory
        if not os.path.exists(f'{x}'):
            # Check if the file already exists in the current directory
            logger.info(
                f"Checking if the {x} zip file already exists in the current directory...")
            if not os.path.exists(f'{x}.zip'):
                # Send a request to the URL and save the response
                logger.info(
                    f"Sending a request to and saving the url response...")
                response = requests.get(y)

                # Write the contents of the response to a file
                with open(f'{x}.zip', 'wb') as f:
                    logger.info(f'writing the content to {x} file..')
                    f.write(response.content)

            # Unzip the downloaded file
            with zipfile.ZipFile(f'{x}.zip', 'r') as zip_ref:
                logger.info(f'Unzipping the downloaded file{x}.zip file...')
                zip_ref.extractall()

            # Rename the unzipped directory to 'table names'
            os.replace(z, f'{x}')

            # Delete the zip file
            os.remove(f'{x}.zip')

        else:
            logger.info(
                f"Directory {x} already exists. No need to download or unzip.")
            if os.path.isdir(f'{x}.zip'):
                # Delete the zip file
                os.remove(f'{x}.zip')

    files = ['/app/water_polygons/water_polygons.shp',
             '/app/land_polygons/land_polygons.shp']
    table = ['water_polygons', 'land_polygons']

    for file, table in zip(files, table):

        # Check if the table already exists in the database
        logger.info(
            f'Inspecting the table {table} and saving the tables to the database....')
        if table in inspector.get_table_names(schema="public"):
            logger.info(
                f'{table} table already exists in the database. Skipping...')
        else:

            # Read the shapefile into a GeoDataFrame
            logger.info(
                f'Reading the {file} and saving to the table {table}....')
            gdf = gpd.read_file(file)

            # Write the GeoDataFrame to the database
            gdf.to_postgis(table, engine, if_exists='replace')
            logger.info(f'Saved {table} to PostGIS')


check_for_schema()  # run pgsnapshot schema

# Downloading the osm data from geofabrik portal in pbf format
# download_files(european_urls)
# read_pbf_files(seamarks_list1)


# check if the file 'world.osm' exists in the current directory
if os.path.exists("/tmp/data.osm"):
    print("world.osm exists in current directory")
else:
    print("world.osm does not exist in current directory. Downloading...")
    download_world_seamarks()

read_xml_files(['/tmp/data.osm'])
save_shp_coastlines_water()
