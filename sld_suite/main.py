import os
import requests

if not os.path.isdir('./xml'):
    os.makedirs('./xml')

import heatmaps
import depths
import wind
import wave_dir
import pressure


def putSLDs(path, admin, password, url):
    filepaths = [os.path.join(path, file) for file in os.listdir(path)]

    for filepath in filepaths:
        styleName = os.path.splitext(os.path.basename(filepath))[0]
        post = requests.post(url=f"{url}/styles",
                             data=f"<style><name>{styleName}</name><filename>{styleName}.sld</filename></style>",
                             auth=(admin, password),
                             headers={'content-type': 'application/xml'})

        with open(filepath) as f:
            sld_data = f.read()
            put = requests.put(url=f"{url}/styles/{styleName}",
                               data=sld_data,
                               auth=(admin, password),
                               headers={'content-type': 'application/vnd.ogc.sld+xml'},
                               params={'file': filepath})


putSLDs(path='./xml',
        admin='admin',
        password='geoserver',
        url='http://localhost/geoserver/rest')
