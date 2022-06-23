import argparse
import shutil

import json
import os
import time

import rasterio
from utils.gdal_process import proj, build_merge_vrt, clip_by_geometry


def main(opts):
    files = []
    if vars(opts)["input_files"] is not None:
        files = vars(opts)["input_files"]
    elif "input_folder" in vars(opts) is not None:
        input_folder = os.path.abspath(vars(opts)["input_folder"])
        folder_files = os.listdir(input_folder)
        for f in folder_files:
            if f[-3:] == "tif":
                files.append(os.path.join(input_folder, f))

    temp = os.path.abspath(vars(opts)["temp_folder"])
    os.makedirs(temp, exist_ok=True)

    # 转投影, 输出为投影epsg：4326
    proj_files = []
    # 此处可并行处理
    for file in files:
        proj_files.append(proj(file, output=temp))

    # 生成tiles产品
    if vars(opts)["product_folder"] is not None:
        product_dir = os.path.abspath(vars(opts)["product_folder"])
        os.makedirs(product_dir, exist_ok=True)
        produce_3_degrees(proj_files, output=product_dir, temp=temp)

    shutil.rmtree(temp)


def produce_3_degrees(input_files, output, temp, tag='Lake'):
    tile_file_map = get_tile_file_map(input_files)
    for tile_name, file_map in tile_file_map.items():
        # 此处可并行处理
        vrt = build_merge_vrt(file_map['files'], temp, tag=tile_name + '_')
        geom = get_element_from_bounds(file_map['bounds'])
        f_name = os.path.join(output, tile_name + '_' + tag + '.tif')
        clip_by_geometry(vrt, geom, f_name)
        print(f_name + '已生成。')


# 根据四至点坐标获得geometry
def get_element_from_bounds(bounds):
    lt = [bounds[0], bounds[1]]
    rt = [bounds[2], bounds[1]]
    lb = [bounds[0], bounds[3]]
    rb = [bounds[2], bounds[3]]
    geometry = {'type': 'Polygon', 'coordinates': [[lt, rt, rb, lb]]}
    return geometry


def get_tile_file_map(input_files: list):
    tile_file_map = {}  # k:tile name such as S01E01 ;v:{bounds:bounds,files:files}

    with open("etc/tiles_3degrees.json") as f:
        tile_bounds = json.load(f)  # k:tile name;,v:bounds

    for f in input_files:
        with rasterio.open(f) as rio:
            left, top, right, bottom = rio.bounds
            for tile_name, bounds in tile_bounds.items():
                if (bounds[0] <= left <= bounds[2] or bounds[0] >= left >= bounds[2]) and (
                        (bounds[1] <= top <= bounds[3] or bounds[1] >= top >= bounds[3]) or (
                        bounds[1] <= bottom <= bounds[3] or bounds[1] >= bottom >= bounds[3])):
                    if tile_name not in tile_file_map:
                        tile_file_map[tile_name] = {}
                        tile_file_map[tile_name]['bounds'] = bounds
                        tile_file_map[tile_name]['files'] = [f]
                    else:
                        tile_file_map[tile_name]['files'].append(f)
                elif (bounds[0] <= right <= bounds[2] or bounds[0] >= right >= bounds[2]) and (
                        (bounds[1] <= top <= bounds[3] or bounds[1] >= top >= bounds[3]) or (
                        bounds[1] <= bottom <= bounds[3] or bounds[1] >= bottom >= bounds[3])):
                    if tile_name not in tile_file_map:
                        tile_file_map[tile_name] = {}
                        tile_file_map[tile_name]['bounds'] = bounds
                        tile_file_map[tile_name]['files'] = [f]
                    else:
                        tile_file_map[tile_name]['files'].append(f)

    return tile_file_map


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Make product from input files")
    parser.add_argument("-i", "--input_files", dest="input_files", action="extend", nargs="+", help=".tif,...,.tif")
    parser.add_argument("-if", "--input_folder", dest="input_folder", default=None, type=str,
                        help="input folder, can not be used with '-i' at the same time.")
    parser.add_argument("-p", "--product_output", dest="product_folder", default=None, type=str, required=True,
                        help="If product is a directory,make 3 degrees tile product there ")
    parser.add_argument("-t", "--temp", dest="temp_folder", default="./temp", type=str,
                        help="temp folder, default current work path")
    args = parser.parse_args()
    print("当前时间：", time.time())
    time_start = time.time()
    main(args)
    time_end = time.time()
    print('花费时间', time_end - time_start, 's')
#     花费时间 576.0525331497192 s
