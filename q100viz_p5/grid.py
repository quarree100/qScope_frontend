import geopandas
import p5
import shapely

import keystone


class Grid:
    def __init__(self, size, corners):
        self.x_size, self.y_size = size

        # create the corner pin surface for projection
        self.surface = keystone.CornerPinSurface(corners)

        self.polygons = []

        # create polygons
        for i in range(self.x_size):
            for j in range(self.y_size):
                cell = shapely.geometry.Polygon([
                    (i / self.x_size, j / self.y_size),
                    (i / self.x_size, (j + 1) / self.y_size),
                    ((i + 1) / self.x_size, (j + 1) / self.y_size),
                    ((i + 1) / self.x_size, j / self.y_size)
                ])
                self.polygons.append(cell)

    def draw(self, stroke, stroke_weight, fill):
        with p5.push_style():
            p5.stroke(stroke)
            p5.stroke_weight(stroke_weight)
            p5.fill(fill)

            for polygon in self.polygons:
                p5.begin_shape()
                for coord in polygon.exterior.coords:
                    p5.vertex(coord[0] * width, coord[1] * height)
                p5.end_shape()
