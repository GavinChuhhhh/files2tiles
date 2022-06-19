import json

import rasterio

from proj_merge import build_merge_vrt


def produce_3_degrees(input_files, output, temp):
    tile_file_map = get_tile_file_map(input_files)
    for tile_name, files in tile_file_map:

        # merge
        # cut
        #
        pass


def get_tile_file_map(input_files: list):
    tile_file_map = {str: list}  # k:tile name such as S01E01 ;v:files

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
                        tile_file_map[tile_name] = [f]
                    else:
                        tile_file_map[tile_name].append(f)
                elif (bounds[0] <= right <= bounds[2] or bounds[0] >= right >= bounds[2]) and (
                        (bounds[1] <= top <= bounds[3] or bounds[1] >= top >= bounds[3]) or (
                        bounds[1] <= bottom <= bounds[3] or bounds[1] >= bottom >= bounds[3])):
                    if tile_name not in tile_file_map:
                        tile_file_map[tile_name] = [f]
                    else:
                        tile_file_map[tile_name].append(f)

    return tile_file_map
