import argparse
import json
import os
import shutil
import tempfile

from osgeo_utils import gdal2tiles
from osgeo import gdal
from process import build_merge_vrt


def files_xyz_tiles(z_level, f_list: list, output, temp):
    vrt_merge = build_merge_vrt(f_list, output=temp, tag="z" + str(z_level) + "merge_")
    vrt_translate = tempfile.mktemp(suffix='.vrt', prefix="z" + str(z_level) + "translate_", dir=temp)
    translate_options = gdal.TranslateOptions(format="vrt", rgbExpand="rgba",noData=0)
    gdal.Translate(vrt_translate, vrt_merge, options=translate_options)

    gdal2tiles_option = [" ", "-x", "--resampling=near", "--xyz", "--webviewer=leaflet",
                         "--zoom=%s" % z_level, vrt_translate, output]
    gdal2tiles.main(gdal2tiles_option)
