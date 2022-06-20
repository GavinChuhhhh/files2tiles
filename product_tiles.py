import json
import os
import rasterio
from process import build_merge_vrt, clip_by_geometry
from utils.tile_3degrees_json import get_element_from_bounds


def produce_3_degrees(input_files, output, temp,tag='Lake'):
    tile_file_map = get_tile_file_map(input_files)
    for tile_name, file_map in tile_file_map.items():
        vrt = build_merge_vrt(file_map['files'], temp, tag=tile_name+'_')
        geom = get_element_from_bounds(file_map['bounds'])
        f_name = os.path.join(output,tile_name+'_'+tag+'.tif')
        if clip_by_geometry(vrt, geom, f_name):
            print(f_name+'已生成。')



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


# if __name__ == '__main__':
#     tile_file_map = get_tile_file_map(
#         [r"E:\Projects\files2tiles\test\product\temp\T44RMV_20200620T051701_SNR_Lake_epsg4326.tif",
#          r"E:\Projects\files2tiles\test\product\temp\T44RNU_20200602T050659_SNR_Lake_epsg4326.tif"])
#     print(tile_file_map)
