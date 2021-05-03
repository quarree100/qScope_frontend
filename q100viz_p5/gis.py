import geopandas
import p5


class GIS:
    def __init__(self, viewport_extent):
        self.xmin, self.ymin, self.xmax, self.ymax = viewport_extent

        self.width = abs(self.xmax - self.xmin)
        self.height = abs(self.ymax - self.ymin)

    def load_basemap(self, file, extent):
        self.basemap = p5.load_image(file)
        self.basemap_extent = extent
        
    def convert_to_xy(self, x, y):
        self.x_scale = width / self.width
        self.y_scale = height / self.height

        new_x = (int(x) - self.xmin) * self.x_scale
        new_y = height - (int(y) - self.ymin) * self.y_scale

        return (new_x, new_y)

    def draw_basemap(self):
        xmin, ymin, xmax, ymax = self.basemap_extent

        self.x_scale = width / self.width
        self.y_scale = height / self.height

        img_x = int((xmin - self.xmin) * self.x_scale)
        img_y = int((self.ymax - ymax) * self.y_scale)
        img_w = int(abs(xmax - xmin) * self.x_scale)
        img_h = int(abs(ymax - ymin) * self.y_scale)

        p5.image(self.basemap, img_x, img_y, img_w, img_h)

    def draw_linestring_layer(self, df, stroke, stroke_weight):
        p5.push_style()
        p5.stroke(stroke)
        p5.stroke_weight(stroke_weight)
        p5.no_fill()

        for linestring in df.to_dict('records'):
            p5.begin_shape()
            for coord in linestring['geometry'].coords:
                p5.vertex(*self.convert_to_xy(*coord))
            p5.end_shape()

        p5.pop_style()

    def draw_polygon_layer(self, df, stroke, stroke_weight, fill, lerp_target=None, lerp_attr=None):
        p5.push_style()
        p5.stroke(stroke)
        p5.stroke_weight(stroke_weight)

        for polygon in df.to_dict('records'):
            fill_color = fill.lerp(lerp_target, polygon[lerp_attr]) if lerp_target else fill
            p5.fill(fill_color)

            p5.begin_shape()
            for coord in polygon['geometry'].exterior.coords:
                p5.vertex(*self.convert_to_xy(*coord))
            p5.end_shape()

        p5.pop_style()


def read_shapefile(file, layer=None):
    return geopandas.read_file(file, layer=layer).to_crs(epsg=3857)
