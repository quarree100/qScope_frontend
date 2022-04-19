import cv2
import geopandas
import shapely
import pygame

import q100viz.keystone as keystone

crs = "EPSG:3857"


class GIS:
    def __init__(self, canvas_size, src_points, viewport):
        self.surface = keystone.Surface(canvas_size, pygame.SRCALPHA)

        # calculate the projection matrix: EPSG:3857 -> viewport coordinates
        self.surface.src_points = src_points
        self.surface.dst_points = [[0, 0], [0, 100], [100, 100], [100, 0]]
        self.surface.calculate(viewport.transform_mat)

    def get_intersection_indexer(self, df, v_polygon):
        polygon = self.surface.inverse_transform(v_polygon)
        shape = shapely.geometry.Polygon(polygon)

        return df.intersects(shape)

    def draw_linestring_layer(self, surface, df, color, stroke):
        for linestring in df.to_dict('records'):
            points = self.surface.transform(linestring['geometry'].coords)
            pygame.draw.lines(self.surface, pygame.Color(color), False, points, stroke)

    def draw_polygon_layer(self, surface, df, stroke, fill, lerp_target=None, lerp_attr=None):
        try:
            for polygon in df.to_dict('records'):
                if fill:
                    fill_color = pygame.Color(*fill)

                    if lerp_target:
                        target_color = pygame.Color(lerp_target)
                        fill_color = fill_color.lerp(target_color, polygon[lerp_attr])

                points = self.surface.transform(polygon['geometry'].exterior.coords)
                pygame.draw.polygon(self.surface, fill_color, points, stroke)

        except Exception as e:
            session.log += "\n%s" % e


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
