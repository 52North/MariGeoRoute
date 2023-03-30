#!/bin/bash

cat << EOF
------------------------------------------------------
            Open Sea Map Importer
------------------------------------------------------
EOF

echo "db:5432:${POSTGRES_DB}:${POSTGRES_USER}:${POSTGRES_PASSWORD}" > ~/.pgpass && chmod 0600 ~/.pgpass

# Wait until postgres service is running
until psql -h db -U ${POSTGRES_USER} -d ${POSTGRES_DB} -P "pager=off" -c '\l'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

# Check if any data was already imported
if psql -h db -U ${POSTGRES_USER} -d ${POSTGRES_DB} -P "pager=off" -c 'select count(*) from nodes;'; then
  echo "Table 'nodes' already exists - exiting"
  exit 0
else
  echo "Table 'nodes' does not exist - start importing"
fi

# necessary?
#/usr/local/bin/update-postgis.sh

# Set up pgsnapshot database schema
psql -h db -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "create extension hstore;"
psql -h db -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f /osmosis/script/pgsnapshot_schema_0.6.sql
psql -h db -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f /osmosis/script/pgsnapshot_schema_0.6_linestring.sql
psql -h db -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f /osmosis/script/pgsnapshot_schema_0.6_bbox.sql

# Import seamarks data into database
if [[ -e "/tmp/data.osm.pbf" ]]; then
  echo "import data into database using osmosis"
  /osmosis/bin/osmosis --read-pbf file=/tmp/data.osm.pbf \
                       --tf accept-nodes seamark:type=* \
                       --tf reject-ways \
                       --tf reject-relations \
                       --read-pbf file=/tmp/data.osm.pbf \
                       --tf accept-ways seamark:type=* \
                       --used-node \
                       --merge \
                       --write-pgsql host="db" user="${POSTGRES_USER}" password="${POSTGRES_PASSWORD}" database="${POSTGRES_DB}"
fi

if [[ -e "/tmp/data.osm" ]]; then
  echo "import data into database using osmosis"
  /osmosis/bin/osmosis --read-xml file=/tmp/data.osm \
                       --write-pgsql host="db" user="${POSTGRES_USER}" password="${POSTGRES_PASSWORD}" database="${POSTGRES_DB}"
fi

exec "$@"