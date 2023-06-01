from sld import Heatmap

#
# WAVE HEIGHT
#
intervalls = dict(
    smallShip=[-1, 2, 4, 7],
    bigShip=[-1, 5, 9, 13]
)

for steps in intervalls.items():
    wave_height = Heatmap(
        layerName=f'wave_height_{steps[0]}',
        styleName='wave_height',
        catNums=steps[1],
        catColors=['#1ce3ed',
                   '#148818',
                   '#d66604',
                   '#ba0e02']
    )
    wave_height.writeSld()

#
# PRESSURE
#

pressure_heatmap = Heatmap(
    layerName='pressure_heatmap',
    styleName='pressure_heatmap',
    catNums=[98500 + i * 500 for i in range(11)],
    catColors=["#67001F",
               "#B2182B",
               "#D6604D",
               "#F4A582",
               "#FDDBC7",
               "#F7F7F7",
               "#D1E5F0",
               "#92C5DE",
               "#4393C3",
               "#2166AC",
               "#053061"]
)
pressure_heatmap.writeSld()

#
# GUST
#

gust = Heatmap(
    layerName='wind_gust_heatmap',
    styleName='wind_gust_heatmap',
    catNums=[-1, 3, 5, 7],
    catColors=[
        '#1ce3ed',
        '#148818',
        '#d66604',
        '#ba0e02'
    ]
)
gust.writeSld()
