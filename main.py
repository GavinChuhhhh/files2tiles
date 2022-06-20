import argparse
import os
import shutil

import product_tiles
from process import proj
import xyz_tiles


def main(opts):
    files = []
    if vars(opts)["input_files"] is not None:
        files = vars(opts)["input_files"]
    elif "input_folder" in vars(opts) is not None:
        input_folder = os.path.abspath(vars(opts)["input_folder"])
        folder_files = os.listdir(input_folder)
        files = []
        for f in folder_files:
            if f[-3:] == "tif":
                files.append(os.path.join(input_folder, f))

    temp = os.path.abspath(vars(opts)["temp_folder"])
    os.makedirs(temp, exist_ok=True)

    # 转投影, 输出为投影epsg：4326
    proj_files = proj(files, output=temp)

    # 生成tiles产品
    if vars(opts)["product_folder"] is not None:
        product_dir = os.path.abspath(vars(opts)["product_folder"])
        os.makedirs(product_dir,exist_ok=True)
        product_tiles.produce_3_degrees(proj_files, output=product_dir, temp=temp)

    # 生成xyz tiles
    if vars(opts)["xyz_folder"] is not None:
        z_min, z_max = vars(opts)["xyz_zoom"].split("-")
        xyz_folder = os.path.abspath(vars(opts)["xyz_folder"])
        os.makedirs(xyz_folder, exist_ok=True)

        for z_level in range(int(z_min), int(z_max) + 1):
            xyz_tiles.files_xyz_tiles(z_level, proj_files, output=xyz_folder, temp=temp)

    # shutil.rmtree(temp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Make tiles from input files")
    parser.add_argument("-i", "--input_files", dest="input_files", action="extend", nargs="+", help=".tif,...,.tif")
    parser.add_argument("-if", "--input_folder", dest="input_folder", default=None, type=str,
                        help="input folder, can not be used with '-i' at the same time.")
    parser.add_argument("-z", "--zoom", dest="xyz_zoom", default="5-15", type=str,
                        help="This is xyz tile zoom levels, '-z=5-15' for example means that zoom level range from 5 to 15.")
    parser.add_argument("-x", "--xyz_output", dest="xyz_folder", default=None, type=str, help="xyz tiles output folder")
    parser.add_argument("-p", "--product_output", dest="product_folder", default=None, type=str,
                        help="If product is a directory,make 3 degrees tile product there ")
    parser.add_argument("-t", "--temp", dest="temp_folder", default="./temp", type=str,
                        help="temp folder, default current work path")
    args = parser.parse_args()
    main(args)
