import os
import tempfile
from rasterio import mask, warp
import rasterio
from osgeo import gdal
from osgeo_utils import gdal2tiles



def pygdal2tiles(options):
    gdal2tiles.main(options)


def pygdal_translate(input_f, **kwargs):
    arg_rgb = kwargs['rgbExpand'] if 'rgbExpand' in kwargs else 'rgb'
    arg_format = kwargs['format'] if 'format' in kwargs else 'vrt'
    arg_nodata = kwargs['noData'] if 'noData' in kwargs else 0
    translate_options = gdal.TranslateOptions(format=arg_format, rgbExpand=arg_rgb, noData=arg_nodata)
    output_f = os.path.dirname(input_f) + "\\%s_" % arg_rgb + os.path.basename(input_f)+"."+arg_format
    if gdal.Translate(output_f, input_f, options=translate_options) is not None:
        return output_f


def proj(file, output, epsg=4326, form='vrt'):
    projection = "epsg:%s" % epsg
    with rasterio.open(file) as f:
        if f.crs["init"] != "epsg:4326":
            suffix = '.' + form
            proj_f_name = file.split("\\")[-1].replace(".tif", "_epsg" + str(epsg) + suffix)
            proj_file = os.path.join(output, proj_f_name)
            warp_options = gdal.WarpOptions(dstSRS=projection)
            # todo 查看warp不成功error情况
            # 如果输入文件有误
            # TypeError: object of wrong GDALDatasetShadow
            # 如果输出文件已存在，不会报错会直接覆盖。
            # 如果投影dstSRS无法被识别，比如"epsg=4326"误改为"epsg=sag",gdal.WarpOptions会报错
            # ERROR 1: Translating source or target SRS failed
            # TypeError: in method 'wrapper_GDALWarpDestName', argument 4 of type 'GDALWarpAppOptions *'
            if gdal.Warp(proj_file, file, options=warp_options) is not None:
                return proj_file
        else:
            return file


# todo 确认buildvrt最大范围
def build_merge_vrt(f_list: list, output: str, **kw):
    tag = kw['tag']
    if tag is None:
        tag = 'build_merge'
    vrt_merge = tempfile.mktemp(suffix='.vrt', prefix=str(tag), dir=output)

    # resampleAlg= {nearest (default),bilinear,cubic,cubicspline,lanczos,average,mode}
    vrt_options = gdal.BuildVRTOptions(srcNodata=0)
    if gdal.BuildVRT(vrt_merge, f_list, options=vrt_options) is not None:
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
    out_img, out_transform = mask.mask(dataset=data, shapes=roi_polygon_src_coords, all_touched=False, crop=True,
                                       filled=0, pad=False)
    out_meta = data.meta.copy()
    # epsg_code = int(data.crs.data['init'][5:])
    out_meta.update(
        {"driver": "GTiff", "height": out_img.shape[1], "width": out_img.shape[2], "transform": out_transform,
         "crs": data.crs, "compress": 'lzw'}
    )
    data_color = data.colormap(1)

    with rasterio.open(out_tif, "w", **out_meta) as dest:
        dest.write(out_img)
        dest.write_colormap(1, data_color)
