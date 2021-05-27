import sys
import random
import pygame
from pygame.locals import *

import gis
import grid

# geodata sources
BASEMAP_FILE = "../data/Layer/180111-QUARREE100-RK_modifiziert_smaller.jpg"
BUILDINGS_FILE = "../data/Shapefiles/osm_heide_buildings.shp"
WAERMESPEICHER_FILE = "../data/Shapefiles/Wärmespeicher.shp"
HEIZZENTRALE_FILE = "../data/Shapefiles/Heizzentrale.shp"
NAHWAERMENETZ_FILE = "../data/Shapefiles/Nahwärmenetz.shp"
TYPOLOGIEZONEN_FILE = "../data/Shapefiles/Typologiezonen.shp"

# Set FPS
FPS = 10

# Set up colors
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Initialize program
pygame.init()

clock = pygame.time.Clock()

# Set up display
canvas_size = width, height = 1920, 1080
canvas = pygame.display.set_mode(canvas_size)
pygame.display.set_caption("q100viz")

# Initialize geographic viewport and basemap
_gis = gis.GIS(canvas_size,
               [[1013102, 7206177], [1013102, 7207365], [1013936, 7206177], [1013936, 7207365]],
               # southwest          northwest           southeast           northeast
               #                            EPSG:3857 -> surface
               # bottom right       bottom left         top right           top left
               [[width, height],    [0, height],        [width, 0],         [0, 0]])

basemap = gis.Basemap(canvas_size, BASEMAP_FILE, _gis,
                      [[0, 1161],          [0, 0],             [1100, 1161],       [1100, 0]],
                      # bottom left        top left            bottom right        top right
                      #                         image pixels -> EPSG:3857
                      # southwest          northwest           southeast           northeast
                      [[1012695, 7205976], [1012695, 7207571], [1014205, 7205976], [1014205, 7207571]])

# Load data
buildings = gis.read_shapefile(BUILDINGS_FILE, columns={'osm_id': 'int64'}).set_index('osm_id')
buildings['co2'] = [random.random() for row in buildings.values]

typologiezonen = gis.read_shapefile(TYPOLOGIEZONEN_FILE)
nahwaermenetz = gis.read_shapefile(NAHWAERMENETZ_FILE)
waermezentrale = gis.read_shapefile(WAERMESPEICHER_FILE, 'Wärmespeicher').append(gis.read_shapefile(HEIZZENTRALE_FILE))

# Initialize grid
_grid = grid.Grid(canvas_size, 50, 50, 1000, 1000, 11, 11)

# Begin Game Loop
while True:
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN:
            _grid.mouse_pressed()
        elif event.type == QUIT:
            pygame.quit()
            sys.exit()

    _gis.draw_linestring_layer(canvas, nahwaermenetz, (217, 9, 9), 3)
    _gis.draw_polygon_layer(canvas, typologiezonen, 0, (123, 201, 230, 50))
    _gis.draw_polygon_layer(canvas, waermezentrale, 0, (252, 137, 0))
    _gis.draw_polygon_layer(canvas, buildings, 0, (96, 205, 21), (213, 50, 21), 'co2')

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
    _gis.draw_polygon_layer(canvas, buildings[buildings.selected], 2, (255, 0, 127))

    _grid.draw(canvas)

    canvas.blit(basemap.surface, (0, 0))
    canvas.blit(_gis.surface, (0, 0))
    canvas.blit(_grid.surface, (0, 0))

    pygame.display.update()

    clock.tick(FPS)
