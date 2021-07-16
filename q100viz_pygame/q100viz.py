import sys
import threading
import json
import pygame
from pygame.locals import *

import keystone
import gis
import grid
import udp
import stats

# geodata sources
BASEMAP_FILE = "../../data/Layer/180111-QUARREE100-RK_modifiziert_smaller.jpg"
BUILDINGS_OSM_FILE = "../../data/Shapefiles/osm_heide_buildings.shp"
BUILDINGS_DATA_FILE = "../../data/Layer/Gebaeudeliste_import_truncated.csv"
WAERMESPEICHER_FILE = "../../data/Shapefiles/Wärmespeicher.shp"
HEIZZENTRALE_FILE = "../../data/Shapefiles/Heizzentrale.shp"
NAHWAERMENETZ_FILE = "../../data/Shapefiles/Nahwärmenetz.shp"
TYPOLOGIEZONEN_FILE = "../../data/Shapefiles/Typologiezonen.shp"
CSPY_SETTINGS_FILE = '../../settings/cityscopy.json'

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

# UDP
grid_udp_1 = ('localhost', 5000)
grid_udp_2 = ('localhost', 5001)

# Socket.io
stats_io = 'http://localhost:8081'

# Set up display
canvas_size = width, height = 1920, 1080
canvas = pygame.display.set_mode(canvas_size, NOFRAME)
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
               [[1013640, 7207470], [1013000, 7207270], [1013400, 7206120], [1014040, 7206320]],
               viewport)

basemap = gis.Basemap(canvas_size, BASEMAP_FILE,
                      # northwest          southwest           southeast           northeast
                      [[1012695, 7207571], [1012695, 7205976], [1014205, 7205976], [1014205, 7207571]],
                      _gis)
basemap.warp(canvas_size)

# Initialize grid, projected onto the viewport
grid_settings = json.load(open(CSPY_SETTINGS_FILE))['cityscopy']
nrows = grid_settings['nrows']
ncols = grid_settings['ncols']
grid_1 = grid.Grid(canvas_size, nrows, ncols, [[0, 0], [0, 100], [50, 100], [50, 0]], viewport)
grid_2 = grid.Grid(canvas_size, nrows, ncols, [[50, 0], [50, 100], [100, 100], [100, 0]], viewport)

show_basemap = True
show_grid = True

# Load data
buildings = gis.read_shapefile(BUILDINGS_OSM_FILE, columns={'osm_id': 'int64'}).set_index('osm_id')

buildings = stats.append_csv(BUILDINGS_DATA_FILE, buildings, {
    'Wärmeverbrauch 2017 [kWh]': 'float32',
    'Stromverbrauch 2017 [kWh]': 'float32',
})

# data normalized by max values
buildings['Wärme_2017_rel'] = buildings['Wärmeverbrauch 2017 [kWh]'] / buildings.max()['Wärmeverbrauch 2017 [kWh]']
buildings['Strom_2017_rel'] = buildings['Stromverbrauch 2017 [kWh]'] / buildings.max()['Stromverbrauch 2017 [kWh]']

# add cell column
buildings['cell'] = ""
buildings['rotation'] = 0
previous_rotation = buildings['rotation']
buildings['cell_id'] = -1

typologiezonen = gis.read_shapefile(TYPOLOGIEZONEN_FILE)
nahwaermenetz = gis.read_shapefile(NAHWAERMENETZ_FILE)
waermezentrale = gis.read_shapefile(WAERMESPEICHER_FILE, 'Wärmespeicher').append(gis.read_shapefile(HEIZZENTRALE_FILE))

# mask
mask_points = [[0, 0], [100, 0], [100, 100], [0, 100], [0, -50], [-50, -50], [-50, 200], [200, 200], [200, -50], [0, -50]]

# calibration
calibration_mode = False
active_anchor = 0

# UDP server for incoming cspy messages
for grid, grid_udp in [[grid_1, grid_udp_1], [grid_2, grid_udp_2]]:
    udp_server = udp.UDPServer(*grid_udp, 1024)
    udp_thread = threading.Thread(target=udp_server.listen, args=(grid.read_scanner_data,), daemon=True)
    udp_thread.start()

# stats viz communication
_stats = stats.Stats(stats_io)

print(buildings)

# Begin Game Loop
while True:
    # process mouse/keyboard events
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN:
            grid_1.mouse_pressed()
            grid_2.mouse_pressed()
        elif event.type == KEYDOWN:
            # toggle basemap:
            if event.key == K_m:
                show_basemap = event.key == K_m and not show_basemap
            # toggle grid:
            elif event.key == K_g:
                show_grid = not show_grid
            # toggle calibration:
            elif event.key == K_c:
                calibration_mode = not calibration_mode
            if calibration_mode:
                if event.key == K_TAB:
                    active_anchor = 0 if active_anchor == 3 else active_anchor + 1
                elif event.key in [K_UP, K_DOWN, K_RIGHT, K_LEFT]:
                    viewport.src_points[active_anchor][0] += 1 * (event.key == K_LEFT) - 1 * (event.key == K_RIGHT)
                    viewport.src_points[active_anchor][1] += 1 * (event.key == K_UP) - 1 * (event.key == K_DOWN)

                    # recalculate all surface projections
                    viewport.calculate()
                    _gis.surface.calculate(viewport.transform_mat)
                    grid_1.surface.calculate(viewport.transform_mat)
                    grid_2.surface.calculate(viewport.transform_mat)
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
    grid_1.surface.fill(0)
    grid_2.surface.fill(0)

    _gis.draw_linestring_layer(canvas, nahwaermenetz, (217, 9, 9), 3)
    _gis.draw_polygon_layer(canvas, typologiezonen, 0, (123, 201, 230, 50))
    _gis.draw_polygon_layer(canvas, waermezentrale, 0, (252, 137, 0))
    _gis.draw_polygon_layer(canvas, buildings, 0, (96, 205, 21), (213, 50, 21), 'Wärme_2017_rel')

    # find buildings intersecting with selected grid cells
    buildings['selected'] = False

    new_rotation = False

    for grid in [grid_1, grid_2]:
        for y, row in enumerate(grid.grid):
            for x, cell in enumerate(row):
                # buildings.iloc[x, 6] = cell.rot
                if cell.selected:
                    # get viewport coordinates of the cell rectangle
                    cell_vertices = grid.surface.transform(
                        [[_x, _y] for _x, _y in [[x, y], [x + 1, y], [x + 1, y + 1], [x, y + 1]]]
                    )
                    ii = _gis.get_intersection_indexer(buildings, cell_vertices)
                    buildings.loc[ii, 'selected'] = True
                    buildings.loc[ii, 'cell'] = f"{x},{y}"
                    buildings.loc[ii, 'rotation'] = cell.rot
                    buildings.loc[ii, 'cell_id'] = cell.id
                    new_rotation = True

    # print(buildings.iloc[i,5])
    # print(buildings['cell'])
    # print(buildings[buildings['selected'] == True]['cell'].to_markdown())

    # if (previous_rotation != buildings['rotation']):
    #     print("rotation has changed!")
    print(buildings[['cell_id', 'rotation']].to_markdown())
    # print(previous_rotation.compare(buildings['rotation'], keep_equal=True).to_markdown())

    if new_rotation == True:
        previous_rotation = buildings['rotation']

    grid_1.print()

    if len(buildings[buildings.selected]):
        # highlight selected buildings
        _gis.draw_polygon_layer(canvas, buildings[buildings.selected], 2, (255, 0, 127))

    # build clusters of selected buildings and send JSON message
    clusters = stats.make_clusters(buildings[buildings.selected])
    _stats.send_dataframe_as_json(clusters.sum())

    # draw grid
    grid_1.draw(canvas)
    grid_2.draw(canvas)

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
        canvas.blit(grid_1.surface, (0, 0))
        canvas.blit(grid_2.surface, (0, 0))

    pygame.display.update()

    clock.tick(FPS)
