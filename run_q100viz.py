import sys
import random
import threading
import json
import pygame
from pygame.locals import NOFRAME, KEYDOWN, K_c, K_e, K_g, K_m, K_t, K_n, QUIT

from config import config
import q100viz.keystone as keystone
import q100viz.gis as gis
import q100viz.grid as grid
import q100viz.udp as udp
import q100viz.stats as stats
from q100viz.interaction.calibration_mode import CalibrationMode
from q100viz.interaction.edit_mode import EditMode
from q100viz.interaction.tui_mode import TuiMode
import q100viz.session as session

# Set FPS
FPS = 12

# Initialize program
pygame.init()

clock = pygame.time.Clock()

# UDP
grid_udp_1 = ('localhost', 5000)
grid_udp_2 = ('localhost', 5001)

# Socket.io
stats_io = 'http://localhost:8081'

# Set up display
canvas_size = 1920, 1080
canvas = pygame.display.set_mode(canvas_size, NOFRAME)
pygame.display.set_caption("q100viz")

# create the main surface, projected to corner points
# the viewport's coordinates are between 0 and 100 on each axis
viewport = session.viewport = keystone.Surface(canvas_size, pygame.SRCALPHA)
try:
    viewport.load(config['SAVED_KEYSTONE_FILE'])
except Exception:
    print("Failed to open keystone file")
    viewport.src_points = [[0, 0], [0, 100], [100, 100], [100, 0]]
    viewport.dst_points = [[80, 45], [80, 1035], [1840, 1035], [1840, 45]]
viewport.calculate()

# Initialize geographic viewport and basemap

# ROI for distorted polygons:
# _gis = session.gis = gis.GIS(canvas_size,
#                # northeast          northwest           southwest           southeast
#                [[1013622, 7207331], [1013083, 7207150], [1013414, 7206159], [1013990, 7206366]],
#                session.viewport)

_gis = session.gis = gis.GIS(canvas_size,
               # northeast          northwest           southwest           southeast
               [[1013640, 7207470], [1013000, 7207270], [1013400, 7206120], [1014040, 7206320]],
               viewport)

basemap = session.basemap = gis.Basemap(canvas_size, config['BASEMAP_FILE'],
                       # northwest          southwest           southeast           northeast
                       [[1012695, 7207571], [1012695, 7205976], [1014205, 7205976], [1014205, 7207571]],
                       _gis)
basemap.warp()

# Initialize grid, projected onto the viewport
grid_settings = json.load(open(config['CSPY_SETTINGS_FILE']))['cityscopy']
nrows = grid_settings['nrows']
ncols = grid_settings['ncols']
grid_1 = session.grid_1 = grid.Grid(canvas_size, 22, 22, [[0, 0], [0, 100], [50, 100], [50, 0]], viewport)
grid_2 = session.grid_2 = grid.Grid(canvas_size, 22, 22, [[50, 0], [50, 100], [100, 100], [100, 0]], viewport)

show_basemap = False
show_grid = False
show_typologiezonen = False
show_nahwaermenetz = True

# Load data
buildings = gis.read_shapefile(config['BUILDINGS_OSM_FILE'], columns={'osm_id': 'int64'}).set_index('osm_id')

buildings = session.buildings = stats.append_csv(config['BUILDINGS_DATA_FILE'], buildings, {
    'Wärmeverbrauch 2017 [kWh]': 'float32',
    'Stromverbrauch 2017 [kWh]': 'float32',
})

# data normalized by max values
buildings['Wärme_2017_rel'] = buildings['Wärmeverbrauch 2017 [kWh]'] / buildings.max()['Wärmeverbrauch 2017 [kWh]']
buildings['Strom_2017_rel'] = buildings['Stromverbrauch 2017 [kWh]'] / buildings.max()['Stromverbrauch 2017 [kWh]']

# mock data
buildings['CO2'] = [0.5 * random.random() for row in buildings.values]

# add cell column
buildings['cell'] = ""
buildings['selected'] = False

typologiezonen = gis.read_shapefile(config['TYPOLOGIEZONEN_FILE'])
nahwaermenetz = gis.read_shapefile(config['NAHWAERMENETZ_FILE'])
waermezentrale = gis.read_shapefile(config['WAERMESPEICHER_FILE'], 'Wärmespeicher').append(
    gis.read_shapefile(config['HEIZZENTRALE_FILE'])
)

# mask
mask_points = [[0, 0], [100, 0], [100, 100], [0, 100], [0, -50], [-50, -50], [-50, 200], [200, 200], [200, -50], [0, -50]]

# UDP server for incoming cspy messages
for grid, grid_udp in [[grid_1, grid_udp_1], [grid_2, grid_udp_2]]:
    udp_server = udp.UDPServer(*grid_udp, 4096)
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
    # process mouse/keyboard events
    for event in pygame.event.get():
        if active_handler:
            active_handler.process_event(event, config)

        if event.type == KEYDOWN:
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
    viewport.fill(0)
    _gis.surface.fill(0)
    grid_1.surface.fill(0)
    grid_2.surface.fill(0)

    session.gis.draw_linestring_layer(canvas, nahwaermenetz, (217, 9, 9), 3)
    if show_typologiezonen:
        session.gis.draw_polygon_layer(canvas, typologiezonen, 0, (123, 201, 230, 50))
    session.gis.draw_polygon_layer(canvas, waermezentrale, 0, (252, 137, 0))
    session.gis.draw_polygon_layer(canvas, buildings, 0, (96, 205, 21), (213, 50, 21), 'Wärme_2017_rel')  # fill and lerp
    # session.gis.draw_polygon_layer(canvas, buildings, 0, (96, 205, 21), (96, 205, 21), 'Wärme_2017_rel')  # fill all equally
    session.gis.draw_polygon_layer(canvas, buildings, 1, (0, 0, 0), (0, 0, 0), 'Wärme_2017_rel')  # stroke simple black

    # draw grid
    grid_1.draw(canvas)
    grid_2.draw(canvas)

    # draw mask
    pygame.draw.polygon(viewport, (0, 0, 0), viewport.transform(mask_points))

    # draw extras
    if active_handler:
        active_handler.draw(canvas)

    # build clusters of selected buildings and send JSON message
    clusters = stats.make_clusters(buildings[buildings.selected])
    _stats.send_dataframe_as_json(clusters.sum())

    # render surfaces
    if show_basemap:
        canvas.blit(basemap.image, (0, 0))

    canvas.blit(_gis.surface, (0, 0))

    canvas.blit(viewport, (0, 0))

    if show_grid:
        canvas.blit(grid_1.surface, (0, 0))
        canvas.blit(grid_2.surface, (0, 0))

    pygame.display.update()

    clock.tick(FPS)
