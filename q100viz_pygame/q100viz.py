import sys
import random
import threading
import pygame
from pygame.locals import *

import keystone
import gis
import grid
import udp
import stats

# geodata sources
BASEMAP_FILE = "../data/Layer/180111-QUARREE100-RK_modifiziert_smaller.jpg"
BUILDINGS_FILE = "../data/Shapefiles/osm_heide_buildings.shp"
WAERMESPEICHER_FILE = "../data/Shapefiles/Wärmespeicher.shp"
HEIZZENTRALE_FILE = "../data/Shapefiles/Heizzentrale.shp"
NAHWAERMENETZ_FILE = "../data/Shapefiles/Nahwärmenetz.shp"
TYPOLOGIEZONEN_FILE = "../data/Shapefiles/Typologiezonen.shp"

SAVED_KEYSTONE_FILE = 'keystone.save'

# Set FPS
FPS = 12

# Set up colors
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Initialize program
pygame.init()

clock = pygame.time.Clock()

# UDP config
grid_udp = ('localhost', 5000)
stats_udp = ('localhost', 6155)

# Set up display
canvas_size = width, height = 1920, 1080
canvas = pygame.display.set_mode(canvas_size)
pygame.display.set_caption("q100viz")

# create the main surface, projected to corner points
# the viewport's coordinates are between 0 and 100 on each axis
viewport = keystone.Surface(canvas_size, pygame.SRCALPHA)
try:
    viewport.load(SAVED_KEYSTONE_FILE)
except Exception:
    print("Failed to open keystone file")
    viewport.src_points = [[0, 0], [0, 100], [100, 100], [100, 0]]
    viewport.dst_points = [[80, 45], [80, 1035], [1840, 1035], [1840, 45]]
viewport.calculate()

# Initialize geographic viewport and basemap
_gis = gis.GIS(canvas_size,
               # northeast          northwest           southwest           southeast
               [[1013936, 7207365], [1013102, 7207365], [1013102, 7206177], [1013936, 7206177]],
               viewport)

basemap = gis.Basemap(canvas_size, BASEMAP_FILE,
                      # northwest          southwest           southeast           northeast
                      [[1012695, 7207571], [1012695, 7205976], [1014205, 7205976], [1014205, 7207571]],
                      _gis)
basemap.warp(canvas_size)

# Initialize grid, projected onto the viewport
_grid = grid.Grid(canvas_size, 11, 11, [[0, 0], [0, 100], [80, 100], [80, 0]], viewport)

show_basemap = True
show_grid = True

# Load data
buildings = gis.read_shapefile(BUILDINGS_FILE, columns={'osm_id': 'int64'}).set_index('osm_id')
buildings['co2'] = [random.random() for row in buildings.values]

typologiezonen = gis.read_shapefile(TYPOLOGIEZONEN_FILE)
nahwaermenetz = gis.read_shapefile(NAHWAERMENETZ_FILE)
waermezentrale = gis.read_shapefile(WAERMESPEICHER_FILE, 'Wärmespeicher').append(gis.read_shapefile(HEIZZENTRALE_FILE))

# mask
mask_points = [[0, 0], [100, 0], [100, 100], [0, 100], [0, -50], [-50, -50], [-50, 200], [200, 200], [200, -50], [0, -50]]

# calibration
calibration_mode = False
active_anchor = 0

# UDP server for incoming cspy messages
udp_server = udp.UDPServer(*grid_udp, 1024)
udp_thread = threading.Thread(target=udp_server.listen, args=(_grid.read_scanner_data,), daemon=True)
udp_thread.start()

# stats viz communication
_stats = stats.Stats(*stats_udp)

# Begin Game Loop
while True:
    # process mouse/keyboard events
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN:
            _grid.mouse_pressed()
        elif event.type == KEYDOWN:
            if event.key == K_m:
                show_basemap = event.key == K_m and not show_basemap
            elif event.key == K_g:
                show_grid = not show_grid
            elif event.key == K_c:
                calibration_mode = not calibration_mode
            if calibration_mode:
                if event.key == K_TAB:
                    active_anchor = 0 if active_anchor == 3 else active_anchor + 1
                elif event.key in [K_UP, K_DOWN, K_RIGHT, K_LEFT]:
                    viewport.src_points[active_anchor][0] += 0.1 * (event.key == K_LEFT) - 0.1 * (event.key == K_RIGHT)
                    viewport.src_points[active_anchor][1] += 0.1 * (event.key == K_UP) - 0.1 * (event.key == K_DOWN)

                    # recalculate all surface projections
                    viewport.calculate()
                    _gis.surface.calculate(viewport.transform_mat)
                    _grid.surface.calculate(viewport.transform_mat)
                    basemap.surface.calculate(_gis.surface.transform_mat)
                    basemap.warp(canvas_size)
                elif event.key == K_s:
                    viewport.save(SAVED_KEYSTONE_FILE)

        elif event.type == QUIT:
            pygame.quit()
            sys.exit()

    # clear surfaces
    canvas.fill(0)
    viewport.fill(0)
    _gis.surface.fill(0)

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

    if len(buildings[buildings.selected]):
        # highlight selected buildings
        _gis.draw_polygon_layer(canvas, buildings[buildings.selected], 2, (255, 0, 127))

        _stats.send_dataframe_as_json(buildings[buildings.selected])

    # draw grid
    _grid.draw(canvas)

    # draw mask
    pygame.draw.polygon(viewport, BLACK, viewport.transform(mask_points))

    if calibration_mode:
        # draw calibration anchors
        for i, anchor in enumerate(viewport.transform([[0, 0], [0, 100], [100, 100], [100, 0]])):
            pygame.draw.rect(viewport, WHITE,
                             [anchor[0] - 10, anchor[1] - 10, 20, 20],
                             i != active_anchor)

    if show_basemap:
        canvas.blit(basemap.image, (0, 0))

    canvas.blit(_gis.surface, (0, 0))

    canvas.blit(viewport, (0, 0))

    if show_grid:
        canvas.blit(_grid.surface, (0, 0))

    pygame.display.update()

    clock.tick(FPS)
