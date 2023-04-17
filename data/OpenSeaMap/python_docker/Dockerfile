FROM python:3.9-slim-buster

RUN apt-get update \
    && apt-get install -y wget unzip \
    && rm -rf /var/lib/apt/lists/*


RUN apt-get update && apt-get install wget openjdk-11-jre-headless postgresql -y

# Install osmosis (https://wiki.openstreetmap.org/wiki/Osmosis/Installation#Linux)
RUN wget https://github.com/openstreetmap/osmosis/releases/download/0.48.3/osmosis-0.48.3.tgz && \
    mkdir osmosis && \
    mv osmosis-0.48.3.tgz osmosis && \
    cd osmosis && \
    tar xvfz osmosis-0.48.3.tgz && \
    rm osmosis-0.48.3.tgz && \
    chmod a+x bin/osmosis


WORKDIR /app

COPY app/requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Downloaded from https://tiles.openseamap.org/seamark/world.osm
#COPY ./data/world.osm /tmp/data.osm
RUN if [ ! -f /tmp/data.osm ]; then \
    wget http://tiles.openseamap.org/seamark/world.osm -O /tmp/data.osm; \
    fi

COPY . . 

COPY app/ /app


CMD ["python", "./app.py"]

