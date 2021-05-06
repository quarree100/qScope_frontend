import geopandas
import p5
import shapely

import keystone

crs="EPSG:3857"


class GIS:
    def __init__(self, xmin, ymin, xmax, ymax):
        # calculate the projection matrix (EPSG:3857 -> viewport coordinates)
        # note that the viewport origin is at the top!
        self.surface = keystone.CornerPinSurface(
            [[xmin, ymin], [xmin, ymax], [xmax, ymin], [xmax, ymax]   ],
            [[0, height],  [0, 0],       [width, height],   [width, 0]]
        )

    def load_basemap(self, file, xmin, ymin, xmax, ymax):
        self.basemap = p5.load_image(file)

        self.basemap_x = xmin
        self.basemap_y = ymin
        self.basemap_w = xmax - xmin
        self.basemap_h = ymax - ymin

    def get_intersecting_features(self, df, v_polygon):
        polygon = self.surface.inverse_transform(v_polygon)
        shape = shapely.geometry.Polygon(polygon)

        return df[df.intersects(shape)]

    def draw_basemap(self):
        with p5.push_matrix():
            p5.apply_matrix(self.surface.get_transform_mat())

            p5.image(self.basemap,
                     self.basemap_x, self.basemap_y,
                     self.basemap_w, self.basemap_h)

    def draw_linestring_layer(self, df, stroke, stroke_weight):
        with p5.push_matrix():
            p5.apply_matrix(self.surface.get_transform_mat())

            with p5.push_style():
                p5.stroke(stroke)
                p5.stroke_weight(stroke_weight)
                p5.no_fill()

                for linestring in df.to_dict('records'):
                    p5.begin_shape()
                    for coord in linestring['geometry'].coords:
                        p5.vertex(*coord)
                    p5.end_shape()

    def draw_polygon_layer(self, df, stroke, stroke_weight, fill, lerp_target=None, lerp_attr=None):
        with p5.push_matrix():
            p5.apply_matrix(self.surface.get_transform_mat())

            with p5.push_style():
                p5.stroke(stroke)
                p5.stroke_weight(stroke_weight)

                for polygon in df.to_dict('records'):
                    if fill:
                        fill_color = fill.lerp(lerp_target, polygon[lerp_attr]) if lerp_target else fill
                        p5.fill(fill_color)
                    else:
                        p5.no_fill()

                    p5.begin_shape()
                    for coord in polygon['geometry'].exterior.coords:
                        p5.vertex(*coord)
                    p5.end_shape()

def read_shapefile(file, layer=None):
    return geopandas.read_file(file, layer=layer).to_crs(crs=crs)
