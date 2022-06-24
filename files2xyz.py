import argparse
import os
import shutil
import tempfile
import time

from utils.gdal_process import build_merge_vrt, pygdal_translate, pygdal2tiles


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

    z_min, z_max = vars(opts)["xyz_zoom"].split("-")
    xyz_folder = os.path.abspath(vars(opts)["xyz_folder"])

    os.makedirs(xyz_folder, exist_ok=True)

    vrt_merge = build_merge_vrt(files, output=temp, tag="xyz_merge_")

    vrt_translate_rgb = pygdal_translate(vrt_merge, output=temp, format="tif", rgbExpand="rgba", noData=0)
    # vrt_translate_rgb = pygdal_translate(vrt_merge, output=temp, format="vrt", rgbExpand="rgba", noData=0)

    # 此处可并行处理
    for z_level in range(int(z_min), int(z_max) + 1):
        print("正在生成%s缩放等级瓦片." % z_level)
        pygdal2tiles([" ", "-x", "--resampling=near", "--xyz", "--webviewer=leaflet",
                      "--zoom=%s" % z_level, vrt_translate_rgb, xyz_folder])
        print("已生成%s缩放等级瓦片。" % z_level)

    shutil.rmtree(temp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Make tiles from input files")
    parser.add_argument("-i", "--input_files", dest="input_files", action="extend", nargs="+", help=".tif,...,.tif")
    parser.add_argument("-if", "--input_folder", dest="input_folder", default=None, type=str,
                        help="input folder, can not be used with '-i' at the same time.")
    parser.add_argument("-z", "--zoom", dest="xyz_zoom", default="5-15", type=str, required=True,
                        help="This is xyz tile zoom levels, '-z=5-15' for example means that zoom level range from 5 to 15.")
    parser.add_argument("-x", "--xyz_output", dest="xyz_folder", default=None, required=True, type=str,
                        help="xyz tiles output folder")
    parser.add_argument("-t", "--temp", dest="temp_folder", default="./temp", type=str,
                        help="temp folder, default current work path")
    args = parser.parse_args()
    print("当前时间：", time.time())
    time_start = time.time()
    main(args)
    time_end = time.time()
    print('花费时间', time_end - time_start, 's')
#    3-12 花费时间 4094.091322660446 s
#    12花费时间 277.4973180294037 s
