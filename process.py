import os
import tempfile
from rasterio import mask, warp
import rasterio
from osgeo import gdal
from fiona.crs import from_epsg
import pycrs


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


def build_merge_vrt(f_list: list, output: str, **kw):
    tag = kw['tag']
    if tag is None:
        tag = 'merge'
    vrt_merge = tempfile.mktemp(suffix='.vrt', prefix=str(tag), dir=output)

    # resampleAlg= {nearest (default),bilinear,cubic,cubicspline,lanczos,average,mode}
    vrt_options = gdal.BuildVRTOptions(srcNodata=0)
    gdal.BuildVRT(vrt_merge, f_list, options=vrt_options)
    return vrt_merge


def clip_by_geometry(input_f, geom, out_tif, **kwargs):
    if type(input_f) == str and input_f[-3:] == 'vrt':
        data = rasterio.open(input_f)
    elif type(input_f) == list:
        vrt = build_merge_vrt(input_f)
        data = rasterio.open(vrt)
    else:
        raise 'Clip input file type is not correct. '
    roi_polygon_src_coords = warp.transform_geom({'init': 'epsg:4326'},
                                                 data.crs,
                                                 [geom])
    out_img, out_transform = mask.mask(dataset=data, shapes=roi_polygon_src_coords, crop=True,filled=0)
    out_meta = data.meta.copy()
    epsg_code = int(data.crs.data['init'][5:])
    out_meta.update(
        {"driver": "GTiff", "height": out_img.shape[1], "width": out_img.shape[2], "transform": out_transform,
         "crs": pycrs.parse.from_epsg_code(epsg_code).to_proj4()}
        )
    with rasterio.open(out_tif, "w", **out_meta) as dest:
        dest.write(out_img)
    return True
