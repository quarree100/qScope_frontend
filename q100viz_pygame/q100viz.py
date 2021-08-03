import sys
import threading
import json
import pygame
from pygame.locals import *

from config import *
from calibration_mode import CalibrationMode
from edit_mode import EditMode
from tui_mode import TuiMode
import session
import keystone
import gis
import grid
import udp
import stats

# geodata sources
BASEMAP_FILE = "../../data/Layer/180111-QUARREE100-RK_modifiziert_smaller.jpg"
# BUILDINGS_OSM_FILE = "../../data/Shapefiles/osm_heide_buildings.shp"
# BUILDINGS_OSM_FILE = "../../data/Shapefiles/qScope_verzerrt/bestandsgebaeude_verzerrt.shp"
BUILDINGS_OSM_FILE = "export/buildings_export.shp"
BUILDINGS_DATA_FILE = "../../data/Layer/Gebaeudeliste_import_truncated.csv"
WAERMESPEICHER_FILE = "../../data/Shapefiles/Wärmespeicher.shp"
HEIZZENTRALE_FILE = "../../data/Shapefiles/Heizzentrale.shp"
# NAHWAERMENETZ_FILE = "../../data/Shapefiles/Nahwärmenetz.shp"
NAHWAERMENETZ_FILE = "../../data/Shapefiles/qScope_verzerrt/Nahwärmenetz_verzerrt.shp"
TYPOLOGIEZONEN_FILE = "../../data/Shapefiles/Typologiezonen.shp"
CSPY_SETTINGS_FILE = '../../settings/cityscopy.json'

SAVED_KEYSTONE_FILE = 'keystone.save'
SAVED_BUILDINGS_FILE = 'export/buildings_export.shp'

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
canvas = pygame.display.set_mode(canvas_size, NOFRAME)
pygame.display.set_caption("q100viz")

# create the main surface, projected to corner points
# the viewport's coordinates are between 0 and 100 on each axis
session.viewport = keystone.Surface(canvas_size, pygame.SRCALPHA)
try:
    session.viewport.load(SAVED_KEYSTONE_FILE)
except Exception:
    print("Failed to open keystone file")
    session.viewport.src_points = [[0, 0], [0, 100], [100, 100], [100, 0]]
    session.viewport.dst_points = [[80, 45], [80, 1035], [1840, 1035], [1840, 45]]
session.viewport.calculate()

# Initialize geographic viewport and basemap
session.gis = gis.GIS(canvas_size,
               # northeast          northwest           southwest           southeast
               [[1013622, 7207331], [1013083, 7207150], [1013414, 7206159], [1013990, 7206366]],
               session.viewport)

session.basemap = gis.Basemap(canvas_size, BASEMAP_FILE,
                      # northwest          southwest           southeast           northeast
                      [[1012695, 7207571], [1012695, 7205976], [1014205, 7205976], [1014205, 7207571]],
                      session.gis)
session.basemap.warp(canvas_size)

# Initialize grid, projected onto the viewport
grid_settings = json.load(open(CSPY_SETTINGS_FILE))['cityscopy']
nrows = grid_settings['nrows']
ncols = grid_settings['ncols']
session.grid_2 = grid.Grid(canvas_size, 22, 22, [[0, 0], [0, 100], [50, 100], [50, 0]], session.viewport)
session.grid_1 = grid.Grid(canvas_size, 22, 22, [[50, 0], [50, 100], [100, 100], [100, 0]], session.viewport)

show_basemap = False
show_grid = False
show_typologiezonen = False
show_nahwaermenetz = True

# Load data
buildings = gis.read_shapefile(BUILDINGS_OSM_FILE, columns={'osm_id': 'int64'}).set_index('osm_id')

buildings = session.buildings = stats.append_csv(BUILDINGS_DATA_FILE, buildings, {
    'Wärmeverbrauch 2017 [kWh]': 'float32',
    'Stromverbrauch 2017 [kWh]': 'float32',
})

# data normalized by max values
buildings['Wärme_2017_rel'] = buildings['Wärmeverbrauch 2017 [kWh]'] / buildings.max()['Wärmeverbrauch 2017 [kWh]']
buildings['Strom_2017_rel'] = buildings['Stromverbrauch 2017 [kWh]'] / buildings.max()['Stromverbrauch 2017 [kWh]']

# add cell column
buildings['cell'] = ""
buildings['selected'] = False

typologiezonen = gis.read_shapefile(TYPOLOGIEZONEN_FILE)
nahwaermenetz = gis.read_shapefile(NAHWAERMENETZ_FILE)
waermezentrale = gis.read_shapefile(WAERMESPEICHER_FILE, 'Wärmespeicher').append(gis.read_shapefile(HEIZZENTRALE_FILE))

# mask
mask_points = [[0, 0], [100, 0], [100, 100], [0, 100], [0, -50], [-50, -50], [-50, 200], [200, 200], [200, -50], [0, -50]]

# UDP server for incoming cspy messages
for grid, grid_udp in [[session.grid_1, grid_udp_1], [session.grid_2, grid_udp_2]]:
    udp_server = udp.UDPServer(*grid_udp, 1024)
    udp_thread = threading.Thread(target=udp_server.listen, args=(grid.read_scanner_data,), daemon=True)
    udp_thread.start()

# stats viz communication
_stats = stats.Stats(stats_io)

print(buildings)

handlers = {
    'calibrate': CalibrationMode(),
    'edit': EditMode(),
    'tui': TuiMode()
}
active_handler = handlers['tui']

# Begin Game Loop
while True:
    ################## process mouse/keyboard events ##################
    for event in pygame.event.get():
        if active_handler:
            active_handler.process_event(event)

        if event.type == MOUSEBUTTONDOWN:
            session.grid_1.mouse_pressed()
            session.grid_2.mouse_pressed()
        elif event.type == KEYDOWN:
            # toggle basemap:
            if event.key == K_m:
                show_basemap = event.key == K_m and not show_basemap
            # toggle grid:
            elif event.key == K_g:
                show_grid = not show_grid
            # toggle typologiezonen:
            if event.key == K_t:
                show_typologiezonen = not show_typologiezonen
            # toggle nahwaermenetz:
            if event.key == K_n:
                show_nahwaermenetz = not show_nahwaermenetz                
            # toggle calibration:
            elif event.key == K_c:
                active_handler = handlers['calibrate' if active_handler != handlers['calibrate'] else 'tui']
            # toggle edit-mode to move polygons:
            elif event.key == K_e:
                active_handler = handlers['edit' if active_handler != handlers['edit'] else 'tui']

        elif event.type == QUIT:
            pygame.quit()
            sys.exit()

    # clear surfaces
    canvas.fill(0)
    session.viewport.fill(0)
    session.gis.surface.fill(0)
    session.grid_1.surface.fill(0)
    session.grid_2.surface.fill(0)

    session.gis.draw_linestring_layer(canvas, nahwaermenetz, (217, 9, 9), 3)
    if show_typologiezonen:
        session.gis.draw_polygon_layer(canvas, typologiezonen, 0, (123, 201, 230, 50))
    session.gis.draw_polygon_layer(canvas, waermezentrale, 0, (252, 137, 0))
    # session.gis.draw_polygon_layer(canvas, buildings, 0, (96, 205, 21), (213, 50, 21), 'Wärme_2017_rel')  # fill
    session.gis.draw_polygon_layer(canvas, buildings, 0, (96, 205, 21), (96, 205, 21), 'Wärme_2017_rel')  # fill
    session.gis.draw_polygon_layer(canvas, buildings, 1, (0, 0, 0), (0, 0, 0), 'Wärme_2017_rel')  # stroke simple black

    # build clusters of selected buildings and send JSON message
    clusters = stats.make_clusters(buildings[buildings.selected])
    _stats.send_dataframe_as_json(clusters.sum())

    # draw grid
    session.grid_1.draw(canvas)
    session.grid_2.draw(canvas)

    # draw mask
    pygame.draw.polygon(session.viewport, BLACK, session.viewport.transform(mask_points))

    if active_handler:
        active_handler.draw(canvas)

    if show_basemap:
        canvas.blit(session.basemap.image, (0, 0))

    canvas.blit(session.gis.surface, (0, 0))

    canvas.blit(session.viewport, (0, 0))

    if show_grid:
        canvas.blit(session.grid_1.surface, (0, 0))
        canvas.blit(session.grid_2.surface, (0, 0))

    pygame.display.update()

    clock.tick(FPS)
