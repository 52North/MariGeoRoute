import argparse
import os
import requests

import heatmaps
import depths
import wind
import wave_dir
import pressure


AVAILABLE_GROUPS = ['depths', 'heatmaps', 'pressure', 'wave_dir', 'wind']


def parse_parameter() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Create sld files and optionally upload them to GeoServer.')
    parser.add_argument('-f', '--folder',
                        help="Folder where the xml files are stored. Defaults to './xml'.",
                        required=False, type=str, default='./xml')
    parser.add_argument('-g', '--groups',
                        help="Groups to be used. Pass as space-separated list. Available options are: 'depths', 'wave_dir', 'wind', 'heatmaps' and 'pressure'. Defaults to all.",
                        required=False, type=str, nargs='+', default=AVAILABLE_GROUPS)
    parser.add_argument('--upload',
                        help="Whether the sld files should be uploaded to GeoServer. <True|False>. Defaults to 'True'.",
                        required=False, type=str, default='True')
    parser.add_argument('--url',
                        help="GeoServer url. Defaults to 'http://localhost/geoserver/rest'.",
                        required=False, type=str, default='http://localhost/geoserver/rest')
    parser.add_argument('-u', '--user',
                        help="GeoServer user. Defaults to 'admin'.",
                        required=False, type=str, default='admin')
    parser.add_argument('-p', '--password',
                        help="GeoServer password. Defaults to 'geoserver'.",
                        required=False, type=str, default='geoserver')

    args = parser.parse_args()

    #
    #    Post process arguments
    #
    if args.groups:
        for group in args.groups:
            if group not in AVAILABLE_GROUPS:
                print(f"WARNING: {group} is no valid option and will be ignored!")

    upload = str(args.upload).lower()
    if upload == 'true':
        args.upload = True
    elif upload == 'false':
        args.upload = False
    else:
        raise ValueError("--upload does not have a valid value")

    if not os.path.isdir(args.folder):
        print(f"Specified folder '{args.folder}' does not exist. Try creating it.")
        try:
            os.makedirs('./xml')
        except Exception:
            raise

    print("""
    Starting creating sld files and uploading them to GeoServer
    ==============================

    General configuration
    -------------------------------------
    groups      : '{}'
    folder      : '{}'
    upload      : '{}'

    GeoServer configuration
    -------------------------------------
    url         : '{}'
    user        : '{}'
    pass        : '{}'
    """.format(args.groups, args.folder, args.upload, args.url, args.user, len(args.password) * '*'))

    return args


def put_slds(path, url='http://localhost/geoserver/rest', username='admin', password='geoserver'):
    filepaths = [os.path.join(path, file) for file in os.listdir(path)]

    for filepath in filepaths:
        # FIXME: check if style already exists
        # check for exceptions
        styleName = os.path.splitext(os.path.basename(filepath))[0]
        post = requests.post(url=f"{url}/styles",
                             data=f"<style><name>{styleName}</name><filename>{styleName}.sld</filename></style>",
                             auth=(username, password),
                             headers={'content-type': 'application/xml'})

        with open(filepath) as f:
            sld_data = f.read()
            put = requests.put(url=f"{url}/styles/{styleName}",
                               data=sld_data,
                               auth=(username, password),
                               headers={'content-type': 'application/vnd.ogc.sld+xml'},
                               params={'file': filepath})


def main():
    # Parse parameter
    args = parse_parameter()
    # Create xml files
    if 'heatmaps' in args.groups:
        heatmaps.create_xml(args.folder)
    if 'depths' in args.groups:
        depths.create_xml(args.folder)
    if 'wind' in args.groups:
        wind.create_xml(args.folder)
    if 'wave_dir' in args.groups:
        wave_dir.create_xml(args.folder)
    if 'pressure' in args.groups:
        pressure.create_xml(args.folder)
    # Upload styles to GeoServer
    if args.upload:
        put_slds(path=args.folder,
                 username=args.user,
                 password=args.password,
                 url=args.url)


if __name__ == '__main__':
    main()