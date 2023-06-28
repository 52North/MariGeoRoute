import requests


def setDims(newdims):
    res = [f'<coverageDimension><name>{dim}</name></coverageDimension>' for dim in newdims]
    dims= "\n".join(res)
    return(f'<dimensions>{dims}</dimensions>')

def createCoverageXML(coverageName, storeName, workspace, cV=False, cV_var1=None, cV_var2=None, newdims=[], write=False,):
    name =f"""<name>{coverageName}</name>
        <nativeName>{coverageName}</nativeName>
        <namespace>
            <name>{workspace}</name>
        </namespace>
        <title>{coverageName}</title>
        <description>Generated from ImageMosaic</description>
        <keywords>
            <string>{coverageName}</string>
            <string>WCS</string>
            <string>ImageMosaic</string>
        </keywords>
        <enabled>true</enabled>"""

    xmin=-180
    xmax=180
    ymin=-90
    ymax=90

    crs =f"""<nativeCRS>GEOGCS['WGS 84',
      DATUM['World Geodetic System 1984',
        SPHEROID['WGS 84', 6378137.0, 298.257223563, AUTHORITY['EPSG','7030']],
        AUTHORITY['EPSG','6326']],
      PRIMEM['Greenwich', 0.0, AUTHORITY['EPSG','8901']],
      UNIT['degree', 0.017453292519943295],
      AXIS['Geodetic longitude', EAST],
      AXIS['Geodetic latitude', NORTH],
      AUTHORITY['EPSG','4326']]</nativeCRS>
        <srs>EPSG:4326</srs>
        <nativeBoundingBox>
            <minx>{xmin}</minx>
            <maxx>{xmax}</maxx>
            <miny>{ymin}</miny>
            <maxy>{ymax}</maxy>
            <crs>EPSG:4326</crs>
        </nativeBoundingBox>
        <latLonBoundingBox>
            <minx>{xmin}</minx>
            <maxx>{xmax}</maxx>
            <miny>{ymin}</miny>
            <maxy>{ymax}</maxy>
            <crs>EPSG:4326</crs>
        </latLonBoundingBox>
        <projectionPolicy>REPROJECT_TO_DECLARED</projectionPolicy>"""

    timeDim=f"""<entry key="time">
                <dimensionInfo>
                    <enabled>true</enabled>
                    <presentation>LIST</presentation>
                    <units>ISO8601</units>
                    <defaultValue>
                        <strategy>MINIMUM</strategy>
                    </defaultValue>
                    <nearestMatchEnabled>true</nearestMatchEnabled>
                    <rawNearestMatchEnabled>false</rawNearestMatchEnabled>
                </dimensionInfo>
            </entry>"""
    dir =f"""<entry key="dirName">{storeName}_{coverageName}</entry>"""
    if cV:
        coverageView=f"""<entry key="COVERAGE_VIEW">
                <coverageView>
                    <coverageBands>
                        <coverageBand>
                            <inputCoverageBands class="singleton-list">
                                <inputCoverageBand>
                                    <coverageName>{cV_var1}</coverageName>
                                </inputCoverageBand>
                            </inputCoverageBands>
                            <definition>{cV_var1}</definition>
                            <index>0</index>
                            <compositionType>BAND_SELECT</compositionType>
                        </coverageBand>
                        <coverageBand>
                            <inputCoverageBands class="singleton-list">
                                <inputCoverageBand>
                                    <coverageName>{cV_var2}</coverageName>
                                </inputCoverageBand>
                            </inputCoverageBands>
                            <definition>{cV_var2}</definition>
                            <index>1</index>
                            <compositionType>BAND_SELECT</compositionType>
                        </coverageBand>
                    </coverageBands>
                    <name>{coverageName}</name>
                    <envelopeCompositionType>INTERSECTION</envelopeCompositionType>
                    <selectedResolution>BEST</selectedResolution>
                    <selectedResolutionIndex>-1</selectedResolutionIndex>
                </coverageView>
            </entry>"""
    else:
        coverageView=''

    metadata=f"""<metadata>{timeDim}{dir}{coverageView}</metadata>"""


    store=f"""<store class="coverageStore">
            <name>{workspace}:{storeName}</name>
        </store>"""


    if not newdims:
        dim = ''
    else:
        dim =setDims(newdims)

    coverage=f"""<coverage>{name}{crs}{metadata}{store}{dim}<nativeCoverageName>{coverageName}</nativeCoverageName>
    </coverage>"""
    if write:
        with open(f'{coverageName}.xml', 'w+') as file:
            file.write(coverage)
    return(coverage)

def postCoverages(admin, password, url, data):
    r = requests.post(url, auth=(admin, password), data=data, headers = {'content-type' : 'text/xml'})
    print(r.status_code)

resturl="http://maridata.dev.52north.org/geoserver/rest"
resturl="http://localhost/geoserver/rest"

def createCoverages(baseURL, password, coverageName, storeName, workspace, cV=False, cV_var1=None, cV_var2=None, newdims=[], write=False, user = 'admin'):
    url=f"""{baseURL}/workspaces/{workspace}/coveragestores/{storeName}/coverages"""
    postCoverages(user, password, url, createCoverageXML(coverageName, storeName, workspace, cV, cV_var1, cV_var2, newdims, write))

layers = dict(
    waves = ["VHM0","VTPK","VMDR"],
    physics = ["thetao","so","zos"],
    weather = ["Temperature_surface","Pressure_reduced_to_MSL_msl","Wind_speed_gust_surface"]
)
coverageViews = dict(
    current = dict(
        store = 'currents',
        cV = ["utotal", "vtotal"],
        newdims=[]
    ),
    windbarbs = dict(
        store= 'weather',
        cV=["u-component_of_wind_height_above_ground","v-component_of_wind_height_above_ground"],
        newdims = ['u', 'v']
    )
)

pairs = [ (item[0], variable) for item in layers.items() for variable in item[1]]

for pair in pairs:
    storeName, coverageName = pair
    createCoverages(resturl, 'geoserver', coverageName, storeName, 'geonode')

for key in coverageViews.keys():
    view = coverageViews[key]
    createCoverages(resturl, 'geoserver', key, view['store'], 'geonode', True, view['cV'][0], view['cV'][1], view['newdims'], True)