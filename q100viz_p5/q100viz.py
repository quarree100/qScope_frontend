import p5
import pathlib
import random
import threading

import gis
import grid
import keystone
import stats
import udp

path = pathlib.Path()

# geodata sources
BASEMAP_FILE = path.joinpath("../data/Layer/180111-QUARREE100-RK_modifiziert_flippedY_smaller.tga")
BUILDINGS_FILE = path.joinpath("../data/Shapefiles/osm_heide_buildings.shp")
BUILDINGS_STATS_FILE = "../data/Gebaeudeliste_import_truncated.csv"
WAERMESPEICHER_FILE = path.joinpath("../data/Shapefiles/Wärmespeicher.shp")
HEIZZENTRALE_FILE = path.joinpath("../data/Shapefiles/Heizzentrale.shp")
NAHWAERMENETZ_FILE = path.joinpath("../data/Shapefiles/Nahwärmenetz.shp")
TYPOLOGIEZONEN_FILE = path.joinpath("../data/Shapefiles/Typologiezonen.shp")

SAVED_KEYSTONE_FILE = 'keystone.save'

# canvas
canvas_size = (1920, 1080) # should match the resolution of the projector
canvas_surface = None
corner_handle = None

# projected surfaces
_gis = None
_grid = None

# geographic area of interest (EPSG:3857)
viewport_extent = dict(xmin=1013102, ymin=7206177, xmax=1013936, ymax=7207365)

# extent of the aerial photo (EPSG:3857)
basemap_extent = dict(xmin=1012695, ymin=7205976, xmax=1014205, ymax=7207571)

# GIS layers (as GeoDataFrame)
typologiezonen = None
buildings = None
waermezentrale = None
nahwaermenetz = None

# UDP config
grid_udp = ('localhost', 5000)
stats_udp = ('localhost', 6155)

_stats = None

# other configuration values
show_basemap = True
show_shapes = True
show_grid = True


def setup():
    global canvas_surface
    global _gis
    global _grid
    global typologiezonen, buildings, waermezentrale, nahwaermenetz
    global _stats

    # initialize canvas before everything else, to make sure the width and height values are available
    p5.size(*canvas_size)

    # calculate the display projection matrix (viewport -> canvas)
    # if a previous surface has been saved, restore it; otherwise use fallback values
    try:
        canvas_surface = keystone.CornerPinSurface(
            [[0, 0], [0, height], [width, height], [width, 0]],
            None
        )
        canvas_surface.load(SAVED_KEYSTONE_FILE)
    except Exception:
        print("Failed to open keystone file")

        canvas_surface = keystone.CornerPinSurface(
            [[0, 0], [0, height], [width, height], [width, 0]],
            [[80, 1035], [1840, 1035], [1840, 45], [80, 45]]
        )

    # ======= GIS setup =======
    _gis = gis.GIS(**viewport_extent)

    _gis.load_basemap(BASEMAP_FILE, **basemap_extent)

    # load shapefiles into data frames
    buildings = gis.read_shapefile(BUILDINGS_FILE, columns={'osm_id': 'int64'}).set_index('osm_id')
    typologiezonen = gis.read_shapefile(TYPOLOGIEZONEN_FILE)
    nahwaermenetz = gis.read_shapefile(NAHWAERMENETZ_FILE)
    waermezentrale = gis.read_shapefile(WAERMESPEICHER_FILE, 'Wärmespeicher').append(gis.read_shapefile(HEIZZENTRALE_FILE))

    # ======= Grid setup =======
    _grid = grid.Grid(150, 50, 1800, 750, 11, 11)

    # ======= UDP server =======
    udp_server = udp.UDPServer(*grid_udp, 1024)
    udp_thread = threading.Thread(target=udp_server.listen, args=(_grid,), daemon=True)
    udp_thread.start()

    # ======= stats viz communication =======
    _stats = stats.Stats(*stats_udp)

    buildings = _stats.append_csv(BUILDINGS_STATS_FILE, buildings, {
        'Straße': 'object',
        'Hausnr.': 'object',
        'Art': 'object',
        'Baujahr': 'Int16', # nullable int
        'Typologie IWU': 'object',
        'WE': 'Int16', # nullable int
        'Gfl. [m²]': 'float64',
        'Sanierung SIZ [u/t/s]': 'object',
        'Energieträger': 'object',
        'Wärmeverbrauch 2017 [kWh]': 'float64',
        'Stromverbrauch 2017 [kWh]': 'float64',
        'Anschluss': 'bool'
    })

    # insert some random values
    buildings['co2'] = [random.random() for row in buildings.values]

    print(buildings.head())
    print(typologiezonen.head())
    print(nahwaermenetz.head())
    print(waermezentrale.head())

    # send min/max values to stats viz
    bmax = buildings.max()
    bmin = buildings.min()

    _stats.send_max_values([
        bmax['co2']
    ], [
        bmin['co2']
    ])


def draw():
    global corner_handle

    p5.background(0)

    with p5.push_matrix():
        p5.apply_matrix(canvas_surface.get_transform_mat())

        # GIS shapes and objects
        if show_basemap:
            _gis.draw_basemap()

        if show_shapes:
            _gis.draw_polygon_layer(buildings, 0, 1, p5.Color(96, 205, 21), p5.Color(213, 50, 21), 'co2')
            _gis.draw_polygon_layer(typologiezonen, 0, 1, p5.Color(123, 201, 230, 50))
            _gis.draw_linestring_layer(nahwaermenetz, p5.Color(217, 9, 9), 3)
            _gis.draw_polygon_layer(waermezentrale, 0, 1, p5.Color(252, 137, 0))

            # find buildings intersecting with selected grid cells
            buildings['selected'] = False

            for y, row in enumerate(_grid.grid):
                for x, cell in enumerate(row):
                    if cell.selected:
                        # get viewport coordinates of the cell rectangle
                        cell_vertices = _grid.surface.transform(
                            [[_x, _y] for _x, _y in [[x, y], [x + 1, y], [x + 1, y + 1], [x, y + 1]]]
                        )
                        ii = _gis.get_intersection_indexer(buildings, cell_vertices)
                        buildings.loc[ii, 'selected'] = True

            # highlight selected buildings
            _gis.draw_polygon_layer(buildings[buildings.selected], p5.Color(255, 0, 127), 2, None)

        # grid
        if show_grid:
            _grid.draw(p5.Color(255, 255, 255), 1)

        # mask
        border = 1000
        with p5.push_style():
            p5.fill(p5.Color(0, 0, 0))
            p5.rect(-border, -border, width + 2 * border, border)
            p5.rect(-border, height, width + 2 * border, height + border)
            p5.rect(-border, -border, border, height + 2 * border)
            p5.rect(width, -border, width + border, height + 2 * border)

    # get the drag handle (if the mouse hovers over it)
    corner_handle = canvas_surface.get_corner_handle(20)

    if corner_handle:
        with p5.push_style():
            p5.no_stroke()
            p5.fill(p5.Color(255, 255, 255, 200))
            p5.circle(list(corner_handle)[0], list(corner_handle)[1], 20)


# Mouse event handlers
def mouse_pressed(event):
    # get viewport coordinate
    mouse_position = canvas_surface.inverse_transform([[event.x, event.y]])[0]

    _grid.mouse_pressed(mouse_position)


def mouse_dragged(event):
    # update corner pin surface while dragging
    if corner_handle:
        canvas_surface.update()


# Keyboard event handlers
def key_typed(event):
    global show_basemap, show_grid

    if event.key.name == 'M':
        show_basemap = not show_basemap
    elif event.key.name == 'G':
        show_grid = not show_grid
    elif event.key.name == 'S':
        canvas_surface.save(SAVED_KEYSTONE_FILE)


if __name__ == '__main__':
    try:
        p5.run(frame_rate=10)
    except KeyboardInterrupt:
        exit()
