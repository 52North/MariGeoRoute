FROM ubuntu:latest

ARG DEBIAN_FRONTEND=noninteractive

ENV POSTGRES_DB=
ENV POSTGRES_USER=
ENV POSTGRES_PASSWORD=

RUN apt-get update && apt-get install wget openjdk-11-jre-headless postgresql -y

# Install osmosis (https://wiki.openstreetmap.org/wiki/Osmosis/Installation#Linux)
RUN wget https://github.com/openstreetmap/osmosis/releases/download/0.48.3/osmosis-0.48.3.tgz && \
    mkdir osmosis && \
    mv osmosis-0.48.3.tgz osmosis && \
    cd osmosis && \
    tar xvfz osmosis-0.48.3.tgz && \
    rm osmosis-0.48.3.tgz && \
    chmod a+x bin/osmosis

# Downloaded from https://download.geofabrik.de/europe/iceland.html
# COPY ./data/iceland-latest.osm.pbf /tmp/data.osm.pbf
# Downloaded from https://tiles.openseamap.org/seamark/world.osm
# COPY ./data/world.osm /tmp/data.osm

COPY ./init-db.sh /init-db.sh

RUN chmod +x /init-db.sh

ENTRYPOINT ["/init-db.sh"]
