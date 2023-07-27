FROM ubuntu:latest

ARG DEBIAN_FRONTEND=noninteractive

ENV POSTGRES_HOST=
ENV POSTGRES_PORT=
ENV POSTGRES_DB=
ENV POSTGRES_SCHEMA=
ENV POSTGRES_USER=
ENV POSTGRES_PASSWORD=

ENV SEAMARKS_FILE=/tmp/world.osm
ENV SEAMARKS_URL=https://tiles.openseamap.org/seamark/world.osm
ENV LAND_POLYGON_SHP=/tmp/land-polygons-complete-4326/land_polygons.shp
ENV LAND_POLYGON_URL=https://osmdata.openstreetmap.de/download/land-polygons-complete-4326.zip
ENV LAND_POLYGON_ZIP=/tmp/land_polygons.zip
ENV WATER_POLYGON_SHP=/tmp/water-polygons-split-4326/water_polygons.shp
ENV WATER_POLYGON_URL=https://osmdata.openstreetmap.de/download/water-polygons-split-4326.zip
ENV WATER_POLYGON_ZIP=/tmp/water_polygons.zip

RUN apt-get update && apt-get install wget unzip openjdk-11-jre-headless postgresql gdal-bin -y

# Install osmosis (https://wiki.openstreetmap.org/wiki/Osmosis/Installation#Linux)
RUN wget https://github.com/openstreetmap/osmosis/releases/download/0.48.3/osmosis-0.48.3.tgz && \
    mkdir osmosis && \
    mv osmosis-0.48.3.tgz osmosis && \
    cd osmosis && \
    tar xvfz osmosis-0.48.3.tgz && \
    rm osmosis-0.48.3.tgz && \
    chmod a+x bin/osmosis

COPY ./init-db.sh /init-db.sh

RUN chmod +x /init-db.sh

ENTRYPOINT ["/init-db.sh"]
