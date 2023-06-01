from sld import WaveDir

colors = dict(
    dark_mode='#c7c7c7',
    light_mode='#000000'
)

for col in colors.items():
    wave_dir = WaveDir()
    wave_dir.layerName = f'wave_dir_{col[0]}'
    wave_dir.fill = col[1]
    wave_dir.stroke = col[1]
    wave_dir.writeSld()
