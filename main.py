import shutil
import argparse
import rasterio
import subprocess
import os
from tile import TileSchema
from osgeo_utils import gdal2tiles


def get_bound(input_file: str):
    with rasterio.open(input_file) as dataset:
        lonlat_bound = []
        left_top = dataset.bounds.left, dataset.bounds.top
        right_bottom = dataset.bounds.right, dataset.bounds.bottom

        if dataset.crs.data['init'] == 'epsg:4326':
            lonlat_bound = [left_top, right_bottom]
        elif dataset.crs.data['init'] == 'epsg:3857':
            lonlat_bound = [TileSchema.google_mercator_to_lonlat(left_top),
                            TileSchema.google_mercator_to_lonlat(right_bottom)]

    return lonlat_bound


def get_tile_file_map(input_folder, z_level):
    tile_file_map = {}

    for f in os.listdir(input_folder):
        pathname = os.path.join(input_folder, f)

        tile = TileSchema()
        bound = get_bound(pathname)
        row_col_list = tile.get_tiles_by_bound(bound, z_level)

        for row, col in row_col_list:
            key = str.join('_', (str(z_level), str(row), str(col)))

            if key not in tile_file_map:
                tile_file_map[key] = []

            tile_file_map[key].append(pathname)

    return tile_file_map


def file2tiles(key, files, output):
    if len(files) > 1:
        file_list = ' '.join(files)
    else:
        file_list = files[0]

    z_level, row, col = key.split('_')

    temp = output + "\\" + 'temp'
    if os.path.exists(temp):
        shutil.rmtree(temp)
    os.mkdir(temp)

    vrt_file = temp + "\\" + key + ".vrt"
    vrt_file1 = temp + "\\" + key + "_tmp.vrt"
    temp_tile = temp + '\\' + z_level + '\\' + row + '\\' + col + '.png'
    output_folder = output + '\\' + z_level + '\\' + row
    output_tile = output + '\\' + z_level + '\\' + row + '\\' + col + '.png'

    cmd_2vrt = 'gdalbuildvrt %s %s' % (vrt_file, file_list)
    subprocess.run(cmd_2vrt)

    # vrt to rgba vrt 的同时裁剪到
    (ulx, uly), (lrx, lry) = TileSchema.get_bound_lonlat_by_row_col(z_level, row, col)
    proj_win_srs = 'EPSG:4326'
    cmd_vrt2vrt = 'gdal_translate -of vrt ' \
                  '-projwin %f %f %f %f -projwin_srs %s ' % (ulx, uly, lrx, lry, proj_win_srs) + \
                  '-expand rgba %s %s' % (vrt_file, vrt_file1)
    subprocess.run(cmd_vrt2vrt)

    # --resampling=near: nearest neighbour resampling (fastest algorithm, worst interpolation quality).
    arg_list = [' ', '--resampling=near', '-q', '--xyz', '--processes=2', '--webviewer=none',
                '--zoom=%s' % z_level, vrt_file1, temp]
    print('正在生成%s' % output_tile)
    gdal2tiles.main(arg_list)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    shutil.copyfile(temp_tile, output_tile)

    shutil.rmtree(temp)


def main(opts):
    input_folder = os.path.abspath(vars(opts)['input_folder'])
    z_min, z_max = vars(opts)['zoom'].split('-')
    output = os.path.abspath(vars(opts)['output'])

    # 获得缩放、瓦片行列号与输入文件的映射字典
    for z_level in range(int(z_min), int(z_max) + 1):
        tile_file_map = get_tile_file_map(input_folder, z_level)

        for key, files in tile_file_map.items():
            file2tiles(key, files, output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Make tiles from a tiff input files' folder")
    parser.add_argument("-i", "--input", dest="input_folder", default=None, type=str, help="tiff input files' folder")
    parser.add_argument("-z", "--zoom", dest="zoom", default='5-15', type=str,
                        help="This is zoom level, '-z=5-15'for example means that zoom level range from 5 to 15.")
    parser.add_argument("-o", "--output", dest="output", default=None, type=str, help="output folder")
    args = parser.parse_args()
    main(args)
