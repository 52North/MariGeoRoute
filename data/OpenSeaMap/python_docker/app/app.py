import glob
import logging
import os
import shutil
import socket
import time
import zipfile
from contextlib import closing

import geopandas as gpd
import psycopg2
import requests
from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy import inspect

# Configure the logger
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')

# Create a logger instance
logger = logging.getLogger(__name__)


def get_pbf_download_urls():
    """Get pbf download urls from Geofabrik"""

    # Retrieve the metadata from the Geofabrik portal
    response = requests.get('https://download.geofabrik.de/index-v1-nogeom.json')
    metadata = response.json()
    features = metadata['features']

    # Print the URLs for the first 25 dataset files
    for feature in features[:25]:
        urls = feature['properties']['urls']
        # print(urls['pbf'])

    # Print the URLs for European countries
    # print('\nChecking the list of the dataset url for european countries\n')
    european_urls = []
    for feature in features:
        properties = feature['properties']
        urls = properties['urls']
        if (urls['pbf'].split('/')[3] == 'europe' and
                len(urls['pbf'].split('/')) == 5 and
                properties['id'] not in ('dach', 'alps', 'britain-and-ireland')):
            european_urls.append(urls['pbf'])
            # print(urls['pbf'])
    return european_urls


def download_files(urls):
    """Download the European country dataset files"""
    for i, url in enumerate(urls[:2], start=1):
        print(f'Downloading file {i}...')
        local_filename = url.split('/')[-1]
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)


def check_and_install_osmosis(
        osmosis_bin="/osmosis/bin/osmosis",
        osmosis_url="https://github.com/openstreetmap/osmosis/releases/download/0.48.3/osmosis-0.48.3.zip"):
    """Check if osmosis exists and install if it does not exist"""
    if not os.path.exists(osmosis_bin):
        # Install osmosis
        os.makedirs("/osmosis/bin/", exist_ok=True)
        response = requests.get(osmosis_url)
        with open("osmosis.zip", "wb") as f:
            f.write(response.content)
        with zipfile.ZipFile("osmosis.zip", "r") as zip_ref:
            zip_ref.extractall("/osmosis/")
        os.remove("osmosis.zip")
        os.system(f'chmod a+x {osmosis_bin}')


def uninstall_osmosis(osmosis_path="/osmosis"):
    shutil.rmtree(osmosis_path)


def db_table_exists(db_table, db_name, db_user, db_pw, db_host='db', db_port='5432', db_schema='public'):
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_pw,
        host=db_host,
        port=db_port,
        options=f'-c search_path={db_schema}'
    )
    cur = conn.cursor()
    cur.execute(f"select exists(select * from information_schema.tables where table_name='{db_table}')")
    return cur.fetchone()[0]


def check_for_schema(db_name, db_user, db_pw, db_host='db', db_port='5432', db_schema='public'):
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_pw,
        host=db_host,
        port=db_port,
        options=f'-c search_path={db_schema}'
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


def read_pbf_files(seamark_list, db_user, db_pw, db_name, db_host='db', db_port='5432',
                   osmosis_bin='/osmosis/bin/osmosis'):
    # Loop through the list of seamarks files
    for smk in seamark_list:
        # Extract Seamarks from the OSM data using Osmosis
        pbf = smk
        filter_tag = 'accept-nodes'
        filter_tag_way = 'reject-ways'
        seamark = 'seamark:type=*'
        xml = smk[:-4]

        cmd = f'{osmosis_bin} --read-pbf {pbf} --tag-filter {filter_tag_way} --tag-filter {filter_tag} {seamark}  --tag-filter accept-relations --write-pgsql  host={db_host} database={db_name} user={db_user} password={db_pw} validateSchemaVersion=no'
        print(cmd)
        os.system(cmd)


def download_shapefile(name, url, folder):
    # Check if the unzipped directory already exists in the current directory
    if not os.path.exists(f'{name}'):
        # Check if the file already exists in the current directory
        logger.info(
            f"Checking if the {name} zip file already exists in the current directory...")
        if not os.path.exists(f'{name}.zip'):
            # Send a request to the URL and save the response
            logger.info(
                f"Sending a request to and saving the url response...")
            response = requests.get(url)

            # Write the contents of the response to a file
            with open(f'{name}.zip', 'wb') as f:
                logger.info(f'writing the content to {name} file..')
                f.write(response.content)

        # Unzip the downloaded file
        with zipfile.ZipFile(f'{name}.zip', 'r') as zip_ref:
            logger.info(f'Unzipping the downloaded file{name}.zip file...')
            zip_ref.extractall()
        # Rename the unzipped directory to 'table names'
        os.replace(folder, f'{name}')
        # Delete the zip file
        os.remove(f'{name}.zip')
    else:
        logger.info(
            f"Directory {name} already exists. No need to download or unzip.")
        if os.path.isdir(f'{name}.zip'):
            # Delete the zip file
            os.remove(f'{name}.zip')


def download_world_seamarks(file_path='/tmp/data.osm',
                            seamarks_world_url='http://tiles.openseamap.org/seamark/world.osm'):
    response = requests.get(seamarks_world_url)
    with open(file_path, 'wb') as f:
        print(f'Downloading file {seamarks_world_url} started.....')
        f.write(response.content)
        print(f'Downloading file {seamarks_world_url} completed')


def read_xml_files(filenames, db_name, db_user, db_pw, db_host='db', db_port='5432', db_schema='public',
                   osmosis_bin="/osmosis/bin/osmosis", tags='seamark:type=*'):
    for filename in filenames:
        tag_filters = ['accept-nodes', 'accept-ways', 'accept-relations']
        cmd = f'{osmosis_bin} --read-xml file={filename} ' \
              f'--tag-filter {tag_filters[0]} ' \
              f'--tag-filter {tag_filters[1]} ' \
              f'--tag-filter {tag_filters[2]} {tags} ' \
              f'--write-pgsql  host={db_host} database={db_name} user={db_user} ' \
              f'password={db_pw} postgresSchema={db_schema} validateSchemaVersion=no'
        print(cmd)
        os.system(cmd)


def save_shp_land_water(db_name, db_user, db_pw, db_host='db', db_port='5432', db_schema='public'):
    logger.info("Saving shapefiles of land and water polygons and import them into the PostgreSQL database")

    definitions = {
        'land_polygons': {
            'name': 'land_polygons',
            'table': 'land_polygons',
            'file': '/app/land_polygons/land_polygons.shp',
            'url': 'https://osmdata.openstreetmap.de/download/land-polygons-complete-4326.zip',
            'folder': 'land-polygons-complete-4326'
        },
        'water_polygons': {
            'name': 'water_polygons',
            'table': 'water_polygons',
            'file': '/app/water_polygons/water_polygons.shp',
            'url': 'https://osmdata.openstreetmap.de/download/water-polygons-split-4326.zip',
            'folder': 'water-polygons-split-4326'
        }
    }

    # Set up the database connection
    engine = create_engine(f'postgresql://{db_user}:{db_pw}@{db_host}:{db_port}/{db_name}')

    for key, value in definitions.items():
        # Check if the table already exists in the database
        logger.info(
            f"Inspecting the table {value['table']} and saving the tables to the database....")
        if db_table_exists(value['table'], db_name, db_user, db_pw, db_host, db_port, db_schema):
            logger.info(
                f"{value['table']} table already exists in the database. Skipping...")
        else:
            download_shapefile(value['name'], value['url'], value['folder'])
            # Read the shapefile into a GeoDataFrame
            logger.info(
                f"Reading the {value['file']} and saving to the table {value['table']}....")
            gdf = gpd.read_file(value['file'])
            # Write the GeoDataFrame to the database
            gdf.to_postgis(value['table'], engine, schema=db_schema, if_exists='replace')
            logger.info(f"Saved {value['table']} to PostGIS")


def verify_database_connection(db_name: str, db_host: str, db_port: int, db_user: str, db_password: str, no_ping: bool = False)\
        -> bool:
    if not no_ping:
        # ping host
        response = os.system(f"ping -c 1 {db_host} > /dev/null")
        if response == 0:
            logger.info(f"Database host '{db_host}' reachable via ping.")
        else:
            logger.error(f"Could not ping required database host '{db_host}'.")
            return False
    # check host port
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        try:
            if sock.connect_ex((db_host, db_port)) == 0:
                logger.info(f"Database port '{db_port}' on host '{db_host}' is OPEN.")
            else:
                logger.error(f"Database port '{db_port}' on host '{db_host}' is CLOSED.")
                return False
        except socket.gaierror:
            logger.error(f"Hostname '{db_host}' could not be resolved.")
            return False
    # psql connect
    with closing(psycopg2.connect("host={} port={} dbname={} user={} password={}"
                                  .format(db_host, db_port, db_name, db_user, db_password))) as db_conn:
        if db_conn and not db_conn.closed:
            logger.info(f"Database connection to '{db_name}' established")
        else:
            logger.error(f"Could NOT connect to database '{db_name}'")
            return False
    return True


def main():
    # Database connection
    db_host = os.getenv("POSTGRES_HOST") or 'localhost'
    db_port = os.getenv("POSTGRES_PORT") or 5432
    db_schema = os.getenv("POSTGRES_SCHEMA") or 'public'
    db_name = os.getenv("POSTGRES_DB")
    db_user = os.getenv("POSTGRES_USER")
    db_pw = os.getenv("POSTGRES_PASSWORD")

    # Check database connection
    times_slept = 0
    db_conn_ok = False
    max_retries = 15
    sleep = 2
    no_ping = True
    while times_slept < max_retries:
        logger.info(
            "[{}/{}] Check database connection".format(str(times_slept + 1), str(max_retries)))
        if verify_database_connection(db_name, db_host, db_port, db_user, db_pw, no_ping):
            db_conn_ok = True
            break
        time.sleep(sleep)
        times_slept = times_slept + 1

    if not db_conn_ok:
        logger.error("Could not connect to database!")
        exit(1024)

    # # Get the current directory
    # dir_path = os.getcwd()
    #
    # # Create empty list to hold file paths
    # seamarks_list = []
    #
    # # Loop through all files in directory
    # for file in os.listdir(dir_path):
    #     # Check if file is a .pbf file
    #     if file.endswith(".pbf"):
    #         # If file is a .pbf file, append its path to the file_list
    #         seamarks_list.append(os.path.join(dir_path, file))
    #
    # # Replace backlash by forward slash
    # seamarks_list = [p.replace("\\", "/") for p in seamarks_list]
    # print(seamarks_list)

    # Downloading the osm data from geofabrik portal in pbf format
    # european_urls = get_pbf_download_urls()
    # download_files(european_urls)
    # read_pbf_files(seamarks_list)

    if not db_table_exists('ways', db_name, db_user, db_pw, db_host, db_port, db_schema):
        # Check if the file 'world.osm' exists in the current directory
        file_path = "/tmp/data.osm"
        if os.path.exists(file_path):
            logger.info("world.osm exists in current directory")
        else:
            logger.info("world.osm does not exist in current directory. Downloading...")
            download_world_seamarks(file_path)
        # Check and apply pgsnapshot schema
        check_for_schema(db_name, db_user, db_pw, db_host, db_port, db_schema)
        read_xml_files([file_path], db_name, db_user, db_pw, db_host, db_port, db_schema)
    else:
        logger.info("Open Sea Map seamarks data have already been imported. Skipping...")

    save_shp_land_water(db_name, db_user, db_pw, db_host, db_port, db_schema)


if __name__ == '__main__':
    main()
