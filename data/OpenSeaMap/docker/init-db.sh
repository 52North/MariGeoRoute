#!/bin/bash

cat << EOF
------------------------------------------------------
            Open Sea Map Importer
------------------------------------------------------
EOF

# -------------------------------------------------------- #
#                Check database connection                 #
# -------------------------------------------------------- #

echo "${POSTGRES_HOST}:${POSTGRES_PORT}:${POSTGRES_DB}:${POSTGRES_USER}:${POSTGRES_PASSWORD}" > ~/.pgpass && chmod 0600 ~/.pgpass

# Wait until postgres service is running
counter=0
until psql -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -P "pager=off" -c '\l'; do
  if [[ ${counter} -ge ${MAX_RETRIES} ]]; then
    echo "Postgres is unavailable and max retries is reached - exiting"
    exit
  fi
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
  ((counter++))
done

# -------------------------------------------------------- #
#                     Create schema                        #
# -------------------------------------------------------- #

psql -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "CREATE SCHEMA IF NOT EXISTS ${POSTGRES_SCHEMA} AUTHORIZATION \"${POSTGRES_USER}\";";
psql -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "ALTER DATABASE ${POSTGRES_DB} SET search_path = public,${POSTGRES_SCHEMA};";

# necessary?
#/usr/local/bin/update-postgis.sh

# -------------------------------------------------------- #
#                    Import seamarks                       #
# -------------------------------------------------------- #

if psql -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -P "pager=off" -c 'select count(*) from ways;'; then
  echo "Table 'ways' already exists - skipping seamarks data"
else
  echo "Table 'ways' does not exist - start importing seamarks data"

  # Set up pgsnapshot database schema
  psql -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "SET search_path=${POSTGRES_SCHEMA},public; create extension hstore;"
  psql -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "SET search_path=${POSTGRES_SCHEMA},public;" -f /osmosis/script/pgsnapshot_schema_0.6.sql
  psql -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "SET search_path=${POSTGRES_SCHEMA},public;" -f /osmosis/script/pgsnapshot_schema_0.6_linestring.sql
  psql -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "SET search_path=${POSTGRES_SCHEMA},public;" -f /osmosis/script/pgsnapshot_schema_0.6_bbox.sql

  # Download seamarks if they don't exist
  if [[ ! -f ${SEAMARKS_FILE} ]]; then
    wget -q ${SEAMARKS_URL} -O ${SEAMARKS_FILE};
  fi

  # Import seamarks data into database
  if [[ -e ${SEAMARKS_FILE} && ${SEAMARKS_FILE} == *.pbf ]]; then
    echo "import seamarks data into database using osmosis"
    /osmosis/bin/osmosis --read-pbf file=${SEAMARKS_FILE} \
                         --tf accept-nodes seamark:type=* \
                         --tf reject-ways \
                         --tf reject-relations \
                         --read-pbf file=${SEAMARKS_FILE} \
                         --tf accept-ways seamark:type=* \
                         --used-node \
                         --merge \
                         --write-pgsql host="${POSTGRES_HOST}" user="${POSTGRES_USER}" password="${POSTGRES_PASSWORD}" \
                         database="${POSTGRES_DB}" postgresSchema="${POSTGRES_SCHEMA}" validateSchemaVersion=no
  fi

  if [[ -e ${SEAMARKS_FILE} && ${SEAMARKS_FILE} == *.osm ]]; then
    echo "import seamarks data into database using osmosis"
    /osmosis/bin/osmosis --read-xml file=${SEAMARKS_FILE} \
                         --write-pgsql host="${POSTGRES_HOST}" user="${POSTGRES_USER}" password="${POSTGRES_PASSWORD}" \
                         database="${POSTGRES_DB}" postgresSchema="${POSTGRES_SCHEMA}" validateSchemaVersion=no
  fi
fi

# -------------------------------------------------------- #
#            Import land and water polygons                #
# -------------------------------------------------------- #

if psql -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -P "pager=off" -c 'select count(*) from land_polygons;'; then
  echo "Table 'land_polygons' already exists - skipping"
else
  if [[ ! -f ${LAND_POLYGON_SHP} ]]; then
    echo "${LAND_POLYGON_SHP} does not exist - download it"
    if [[ ! -f ${LAND_POLYGON_ZIP} ]]; then
      wget -q ${LAND_POLYGON_URL} -O ${LAND_POLYGON_ZIP};
    fi;
    unzip ${LAND_POLYGON_ZIP} -d /tmp;
    rm ${LAND_POLYGON_ZIP};
  fi
  echo "import land polygons data into database using ogr2ogr"
  ogr2ogr -f PostgreSQL PG:"dbname='${POSTGRES_DB}' host='${POSTGRES_HOST}' port='${POSTGRES_PORT}' user='${POSTGRES_USER}' password='${POSTGRES_PASSWORD}'" ${LAND_POLYGON_SHP} -lco SCHEMA=${POSTGRES_SCHEMA} -lco SPATIAL_INDEX=GIST -nln land_polygons
fi

if psql -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -P "pager=off" -c 'select count(*) from water_polygons;'; then
  echo "Table 'water_polygons' already exists - skipping"
else
  if [[ ! -f ${WATER_POLYGON_SHP} ]]; then
    echo "${WATER_POLYGON_SHP} does not exist - download it"
    if [[ ! -f ${WATER_POLYGON_ZIP} ]]; then
      wget -q ${WATER_POLYGON_URL} -O ${WATER_POLYGON_ZIP};
    fi;
    unzip ${WATER_POLYGON_ZIP} -d /tmp;
    rm ${WATER_POLYGON_ZIP};
  fi
  echo "import water polygons data into database using ogr2ogr"
  ogr2ogr -f PostgreSQL PG:"dbname='${POSTGRES_DB}' host='${POSTGRES_HOST}' port='${POSTGRES_PORT}' user='${POSTGRES_USER}' password='${POSTGRES_PASSWORD}'" ${WATER_POLYGON_SHP} -lco SCHEMA=${POSTGRES_SCHEMA} -lco SPATIAL_INDEX=GIST -nln water_polygons
fi

exec "$@"