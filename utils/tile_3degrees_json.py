import fiona
import json


def get_json():
    map_dict = {}
    for lat in range(-81, 85, 3):
        if lat >= 0:
            lat_tag = 'N' + str(abs(lat))
        else:
            lat_tag = 'S' + str(abs(lat))

        for lon in range(-180, 181, 3):
            if lon <= 0:
                lon_tag = 'E' + str(abs(lon))
                lon_left = lon
                lon_right = lon + 3
            else:
                lon_tag = 'W' + str(abs(lon))
                lon_left = lon
                lon_right = lon - 3

            key = lat_tag + lon_tag
            lat_top = lat
            lat_bottom = lat - 3

            value = [float(lon_left), float(lat_top), float(lon_right), float(lat_bottom)]
            map_dict[key] = value
    data = json.dumps(map_dict, indent=4, separators=(',', ':'))
    with open(r'../etc/tiles_3degrees.json', 'w') as j:
        j.write(data)


def get_shp():
    with open(r'../etc/tiles_3degrees.json') as f:
        data = json.load(f)

    # schema是一个字典结构，指定了geometry及其它属性结构
    schema = {'geometry': 'Polygon',
              'properties': {'id': 'int', 'name': 'str'}}

    # 使用fiona.open方法打开文件，写入数据
    with fiona.open('../etc/tilesby3degree.shp', mode='w', driver='ESRI Shapefile',
                    schema=schema, crs='EPSG:4326', encoding='utf-8') as layer:
        proper_id = 0
        for name, xy in data.items():
            # 从GeoJSON中读取JSON格式的geometry和properties的记录
            proper_id += 1
            geometry = get_element_from_bounds(xy)
            element = {'geometry': geometry, 'properties': {'id': proper_id,
                                                            'name': name}}
            # 写入文件
            layer.write(element)


# 根据四至点坐标获得geometry
def get_element_from_bounds(bounds):
    xy = bounds
    lt = [xy[0], xy[1]]
    rt = [xy[2], xy[1]]
    lb = [xy[0], xy[3]]
    rb = [xy[2], xy[3]]
    geometry = {'type': 'Polygon', 'coordinates': [[lt, rt, rb, lb]]}
    return geometry


if __name__ == '__main__':
    get_json()
    get_shp()
