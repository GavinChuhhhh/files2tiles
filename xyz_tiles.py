import argparse
import json
import os
import shutil

from osgeo_utils import gdal2tiles
from osgeo import gdal
from proj_merge import build_merge_vrt


def files_xyz_tiles(z_level, f_list: list, output, temp):
    vrt_merge = build_merge_vrt(f_list, output=temp, tag=z_level)

    vrt_translate = output + "\\" + str(z_level) + "_translate.vrt"
    translate_options = gdal.TranslateOptions(format="vrt", rgbExpand="rgba")
    gdal.Translate(vrt_translate, vrt_merge, options=translate_options)

    gdal2tiles_option = [" ", "--resampling=near", "--xyz", "--webviewer=leaflet",
                         "--zoom=%s" % z_level, vrt_translate, output]
    gdal2tiles.main(gdal2tiles_option)



