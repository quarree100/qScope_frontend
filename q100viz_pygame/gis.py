import numpy
import geopandas
import pygame

import keystone

crs="EPSG:3857"


class GIS:
    def __init__(self, canvas_size, src_points, dst_points):
        self.surface = keystone.Surface(canvas_size, pygame.SRCALPHA)

        # calculate the projection matrix (EPSG:3857 -> viewport coordinates)
        self.surface.src_points = src_points
        self.surface.dst_points = dst_points
        self.surface.calculate()

    def draw_linestring_layer(self, surface, df, color, stroke):
        for linestring in df.to_dict('records'):
            points = self.surface.transform(linestring['geometry'].coords)
            pygame.draw.lines(self.surface, pygame.Color(color), False, points, stroke)

    def draw_polygon_layer(self, surface, df, stroke, fill, lerp_target=None, lerp_attr=None):
        for polygon in df.to_dict('records'):
            if fill:
                fill_color = pygame.Color(*fill)

                if lerp_target:
                    target_color = pygame.Color(lerp_target)
                    fill_color = fill_color.lerp(target_color, polygon[lerp_attr])

            points = self.surface.transform(polygon['geometry'].exterior.coords)
            pygame.draw.polygon(self.surface, fill_color, points, stroke)


class Basemap:
    def __init__(self, canvas_size, file, gis, src_points, dst_points):
        self.gis = gis
        self.surface = keystone.Surface(canvas_size)

        # calculate the projection matrix (image pixels -> EPSG:3857 -> viewport extent)
        self.surface.src_points = src_points
        self.surface.dst_points = dst_points
        self.surface.calculate()
        self.surface.transform_mat = numpy.dot(self.gis.surface.transform_mat, self.surface.transform_mat)

        # warp image and update the surface
        image = self.surface.warp_image(file, canvas_size)
        self.surface = pygame.image.frombuffer(image, image.shape[1::-1], 'BGR')


def read_shapefile(file, layer=None, columns=None):
    df = geopandas.read_file(file, layer=layer).to_crs(crs=crs)
    if columns:
        df = df.astype(columns)
        return df.loc[:, ['geometry', *columns.keys()]]
    return df
