from math import log, radians, pi, tan, atan, exp, sinh, degrees, asinh


class TileSchema:

    def __init__(self):
        return

    @staticmethod
    def google_mercator_to_lonlat(coordinate):
        semi_axis = 20037508.3427892
        lon = coordinate[0] / semi_axis * 180.0
        lat = 180.0 / pi * (2 * atan(exp(coordinate[1] / semi_axis * 180.0 * pi / 180.0)) - pi / 2)
        return lon, lat

    @staticmethod
    def lonlat_to_google_mercator(geo_ordinate):
        semi_axis = 20037508.3427892
        lat, lon = geo_ordinate
        x = lon * semi_axis / 180.0
        y = log(tan((90.0 + lat) * pi / 360.0)) / (pi / 180.0)
        y = y * semi_axis / 180.0
        return x, y

    @staticmethod
    def get_row_col_by_lonlat(lon, lat, z_level):
        num = 2 ** z_level
        row = int((lon + 180.0) / 360.0 * num)
        col = int((1 - asinh(tan(radians(lat))) / pi) / 2.0 * num)
        if row < 0:
            row = 0
        elif row >= num:
            row = num - 1

        if col < 0:
            col = 0
        elif col >= num:
            col = num - 1

        return row, col

    def get_tiles_by_bound(self, bound, z_level):
        left_top, right_bottom = bound

        start = self.get_row_col_by_lonlat(*left_top, z_level)
        end = self.get_row_col_by_lonlat(*right_bottom, z_level)

        row_col_list = []
        for x in range(start[0], end[0] + 1):
            for y in range(start[1], end[1] + 1):
                row_col_list.append((x, y))
        return row_col_list

    @staticmethod
    def get_lonlat_by_row_col(z_level, row, col):
        n = 2 ** z_level
        lon = row / n * 360.0 - 180.0
        lat = degrees(atan(sinh(pi * (1 - 2 * col / n))))
        return lon, lat

    @staticmethod
    def get_bound_lonlat_by_row_col(z_level, row, col):

        start = TileSchema.get_lonlat_by_row_col(int(z_level), int(row), int(col))
        end = TileSchema.get_lonlat_by_row_col(int(z_level), int(row) + 1, int(col) + 1)
        return start, end
