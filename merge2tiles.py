import argparse
import os
from osgeo_utils import gdal2tiles
from osgeo import gdal


def files2tiles(z_level, files, output):
    vrt_buildvrt = output + "\\" + str(z_level) + "_vrt.vrt"
    vrt_translate = output + "\\" + str(z_level) + "_translate.vrt"

    vrt_options = gdal.BuildVRTOptions()
    gdal.BuildVRT(vrt_buildvrt, files, options=vrt_options)

    translate_options = gdal.TranslateOptions(format="vrt", rgbExpand="rgba")

    gdal.Translate(vrt_translate, vrt_buildvrt, options=translate_options)

    gdal2tiles_option = [' ', '--resampling=near', '--xyz', '--webviewer=leaflet',
                         '--zoom=%s' % z_level, vrt_translate, output]
    gdal2tiles.main(gdal2tiles_option)

    os.remove(vrt_buildvrt)
    os.remove(vrt_translate)


def main(opts):
    files = vars(opts)['input_files']
    z_min, z_max = vars(opts)['zoom'].split('-')
    output = os.path.abspath(vars(opts)['output'])
    os.makedirs(output, exist_ok=True)

    for z_level in range(int(z_min), int(z_max) + 1):
        files2tiles(z_level, files, output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Make tiles from a tiff input files' folder")
    parser.add_argument("-i", "--input", dest="input_files", action="extend", nargs="+", help=".tif,...,.tif")
    parser.add_argument("-z", "--zoom", dest="zoom", default='5-15', type=str,
                        help="This is zoom level, '-z=5-15'for example means that zoom level range from 5 to 15.")
    parser.add_argument("-o", "--output", dest="output", default=None, type=str, help="output folder")
    args = parser.parse_args()
    main(args)
