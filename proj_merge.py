import os

import rasterio
from osgeo import gdal


def proj(files: list, output, epsg=4326):
    proj_files = []
    projection = "epsg:%s" % epsg

    for file in files:
        with rasterio.open(file) as f:
            if f.crs["init"] != "epsg:4326":
                proj_f_name = file.split("\\")[-1].replace(".tif", "_epsg" + str(epsg) + ".tif")
                proj_file = os.path.join(output, proj_f_name)
                warp_options = gdal.WarpOptions(dstSRS=projection)
                # rasterio.warp
                gdal.Warp(proj_file, file, options=warp_options)
                proj_files.append(proj_file)
                continue
            else:
                proj_files.append(file)

    return proj_files


def build_merge_vrt(f_list, output, tag):
    vrt_merge = output + "\\" + str(tag) + ".vrt"
    # resampleAlg= {nearest (default),bilinear,cubic,cubicspline,lanczos,average,mode}
    vrt_options = gdal.BuildVRTOptions(srcNodata=0)
    gdal.BuildVRT(vrt_merge, f_list, options=vrt_options)
    return vrt_merge




