import cv2
import geopandas
import shapely
import pygame

import q100viz.keystone as keystone
from q100viz.settings.config import config
import q100viz.session as session

crs = "EPSG:3857"


class GIS:
    def __init__(self, canvas_size, src_points, viewport):
        self.surface = keystone.Surface(canvas_size, pygame.SRCALPHA)

        # calculate the projection matrix: EPSG:3857 -> viewport coordinates
        self.surface.src_points = src_points
        self.surface.dst_points = [[0, 0], [0, 100], [100, 100], [100, 0]]
        self.surface.calculate(viewport.transform_mat)

        # GIS layers
        self.typologiezonen = read_shapefile(config['TYPOLOGIEZONEN_FILE'])
        self.nahwaermenetz = read_shapefile(config['NAHWAERMENETZ_FILE'])
        self.waermezentrale = read_shapefile(config['WAERMESPEICHER_FILE'], 'Waermespeicher').append(
            read_shapefile(config['HEIZZENTRALE_FILE']))

    def get_intersection_indexer(self, df, v_polygon):
        polygon = self.surface.inverse_transform(v_polygon)
        shape = shapely.geometry.Polygon(polygon)

        return df.intersects(shape)

    def draw_linestring_layer(self, surface, df, color, stroke):
        for linestring in df.to_dict('records'):
            points = self.surface.transform(linestring['geometry'].coords)
            pygame.draw.lines(self.surface, pygame.Color(color), False, points, stroke)


    def draw_polygon_layer(self, surface, df, stroke, fill):
        '''draw polygon layer, do not lerp'''
        try:
            for polygon in df.to_dict('records'):
                if fill:
                    fill_color = pygame.Color(*fill)

                points = self.surface.transform(polygon['geometry'].exterior.coords)
                pygame.draw.polygon(self.surface, fill_color, points, stroke)

        except Exception as e:
            session.log += "\n%s" % e
            print("cannot draw polygon layer: ", e)

    def draw_polygon_layer_bool(self, surface, df, stroke, fill_false, fill_true=None, fill_attr=None):
        '''draw polygon layer, lerp using bool value'''
        try:
            for polygon in df.to_dict('records'):
                if fill_false:
                    fill_color = pygame.Color(*fill_false)

                    if fill_true:
                        fill_color = pygame.Color(fill_true) if polygon[fill_attr] else fill_color

                points = self.surface.transform(polygon['geometry'].exterior.coords)
                pygame.draw.polygon(self.surface, fill_color, points, stroke)

        except Exception as e:
            session.log += "\n%s" % e
            print("cannot draw polygon layer: ", e)

    def draw_polygon_layer_connection_year(self, df, stroke, fill_true, fill_false=None, fill_attr=None):
        '''draw polygon layer, lerp using bool value'''
        try:
            for polygon in df.to_dict('records'):
                fill_color = pygame.Color(fill_true) if polygon[fill_attr] > -1 else fill_false

                points = self.surface.transform(polygon['geometry'].exterior.coords)
                pygame.draw.polygon(self.surface, fill_color, points, stroke)

        except Exception as e:
            session.log += "\n%s" % e
            print("cannot draw polygon layer: ", e)

    def draw_polygon_layer_float(self, surface, df, stroke, fill, lerp_target=None, lerp_attr=None):
        '''draw polygon layer and lerp using float'''
        try:
            for polygon in df.to_dict('records'):
                if fill:
                    fill_color = pygame.Color(*fill)

                    if lerp_target:
                        target_color = pygame.Color(lerp_target)
                        fill_color = fill_color.lerp(target_color, polygon[lerp_attr] / df[lerp_attr].max())

                points = self.surface.transform(polygon['geometry'].exterior.coords)
                pygame.draw.polygon(self.surface, fill_color, points, stroke)

        except Exception as e:
            session.log += "\n%s" % e
            print("cannot draw polygon layer: ", e)

    def draw_buildings_connections(self, df):
        for row in df.to_dict('records'):

            points = self.surface.transform(row['geometry'].exterior.coords)
            centroid = shapely.geometry.Polygon(points).centroid

            target = row['target_point']

            if row['connection_to_heat_grid']:
                pygame.draw.line(
                    self.surface,
                    color=pygame.Color(0, 168, 78),
                    start_pos=((centroid.x, centroid.y)),
                    end_pos=((target.x, target.y)),
                    width=4
                    )

class Basemap:
    def __init__(self, canvas_size, file, dst_points, gis):
        self.canvas_size = canvas_size
        self.file = file
        self.surface = keystone.Surface(canvas_size)

        img_h, img_w, _ = cv2.imread(file).shape

        # calculate the projection matrix (image pixels -> EPSG:3857)
        self.surface.src_points = [[0, 0], [0, img_h], [img_w, img_h], [img_w, 0]],
        self.surface.dst_points = dst_points
        self.surface.calculate(gis.surface.transform_mat)

    def warp(self):
        # warp image and update the surface
        image = self.surface.warp_image(self.file, self.canvas_size)
        self.image = pygame.image.frombuffer(image, image.shape[1::-1], 'BGR')


def read_shapefile(file, layer=None, columns=None):
    df = geopandas.read_file(file, layer=layer).to_crs(crs=crs)
    if columns:
        df = df.astype(columns)
        return df.loc[:, ['geometry', *columns.keys()]]
    return df

def print_shapefile(file, print_each_column=False):
    df = geopandas.read_file(file)
    print("df:", df)
    print("columns: ", df.columns)
    if print_each_column:
        for column in df.columns:
            print(df[column])

def print_geodataframe(df, print_each_column=False):
    print("GeoDataFrame: ", df)
    print("columns: ", df.columns)
    if print_each_column:
        for column in df.columns:
            print(df[column])