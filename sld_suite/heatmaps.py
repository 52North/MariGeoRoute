from sld import Heatmap


def create_xml(outfolder='./xml'):
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
        wave_height.writeSld(outfolder=outfolder)

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
    pressure_heatmap.writeSld(outfolder=outfolder)

    #
    # GUST
    #

    gust = Heatmap(
        layerName='wind_gust_heatmap',
        styleName='wind_gust_heatmap',
        catNums=[-1, 6, 12, 17],
        catColors=[
            '#1ce3ed',
            '#148818',
            '#d66604',
            '#ba0e02'
        ]
    )
    gust.writeSld(outfolder=outfolder)

    #
    # Wave Peak Period (VTPK)
    #

    vtpk = Heatmap(
        layerName='wave_peak_period',
        styleName='wave_peak_period',
        catNums=[5, 10, 15, 17],
        catColors=[
            '#1ce3ed',
            '#148818',
            '#d66604',
            '#ba0e02'
        ]
    )
    vtpk.writeSld(outfolder=outfolder)

    #
    # surface_temp
    #

    surface_temp = Heatmap(
        layerName='surface_temp',
        styleName='surface_temp',
        catNums=[250, 260, 270, 280, 290, 300, 310],
        catColors=['#9d219d',
                   '#4B369D',
                   '#487DE7',
                   '#79C314',
                   '#FAEB36',
                   '#FFA500',
                   '#E81416']

    )
    surface_temp.writeSld(outfolder=outfolder)
