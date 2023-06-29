from sld import Heatmap


def create_xml(outfolder='./xml'):
    #
    # WAVE HEIGHT
    #
    intervals = dict(
        small_ship=[-1, 2, 4, 7],
        big_ship=[-1, 5, 9, 13]
    )
    for steps in intervals.items():
        wave_height = Heatmap(
            layer_name=f'wave_height_{steps[0]}',
            style_name='wave_height',
            cat_nums=steps[1],
            cat_colors=['#1ce3ed',
                       '#148818',
                       '#d66604',
                       '#ba0e02']
        )
        wave_height.write_sld(outfolder=outfolder)

    #
    # PRESSURE
    #

    pressure_heatmap = Heatmap(
        layer_name='pressure_heatmap',
        style_name='pressure_heatmap',
        cat_nums=[98500 + i * 500 for i in range(11)],
        cat_colors=["#67001F",
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
    pressure_heatmap.write_sld(outfolder=outfolder)

    #
    # GUST
    #

    gust = Heatmap(
        layer_name='wind_gust_heatmap',
        style_name='wind_gust_heatmap',
        cat_nums=[-1, 6, 12, 17],
        cat_colors=[
            '#1ce3ed',
            '#148818',
            '#d66604',
            '#ba0e02'
        ]
    )
    gust.write_sld(outfolder=outfolder)

    #
    # Wave Peak Period (VTPK)
    #

    vtpk = Heatmap(
        layer_name='wave_peak_period',
        style_name='wave_peak_period',
        cat_nums=[5, 10, 15, 17],
        cat_colors=[
            '#1ce3ed',
            '#148818',
            '#d66604',
            '#ba0e02'
        ]
    )
    vtpk.write_sld(outfolder=outfolder)

    #
    # surface_temp
    #

    surface_temp = Heatmap(
        layer_name='surface_temp',
        style_name='surface_temp',
        cat_nums=[250, 260, 270, 280, 290, 300, 310],
        cat_colors=['#9d219d',
                   '#4B369D',
                   '#487DE7',
                   '#79C314',
                   '#FAEB36',
                   '#FFA500',
                   '#E81416']

    )
    surface_temp.write_sld(outfolder=outfolder)
