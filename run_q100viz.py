import sys
import os
import random
import threading
import json
import cv2
import pygame
import numpy as np
from pygame.locals import NOFRAME, KEYDOWN, K_c, K_e, K_g, K_m, K_n, K_p, K_s, K_t, K_v, K_PLUS, K_MINUS, QUIT

from config import config
import q100viz.keystone as keystone
import q100viz.gis as gis
import q100viz.grid as grid
import q100viz.udp as udp
import q100viz.stats as stats
from q100viz.interaction.calibration_mode import CalibrationMode
from q100viz.interaction.edit_mode import EditMode
from q100viz.interaction.tui_mode import TuiMode, Slider
from q100viz.interaction.simulation_mode import SimulationMode
import q100viz.session as session

# Set FPS
FPS = session.FPS = 12

# set window position
# os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)

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

_gis = session.gis = gis.GIS(
    canvas_size,
    # northeast          northwest           southwest           southeast
    [[1013631, 7207409], [1012961, 7207198], [1013359, 7205932], [1014029, 7206143]],
    viewport)

basemap = session.basemap = gis.Basemap(
    canvas_size, config['BASEMAP_FILE'],
    # northwest          southwest           southeast           northeast
    [[1012695, 7207571], [1012695, 7205976], [1014205, 7205976], [1014205, 7207571]],
    _gis)
basemap.warp()

# Initialize grid, projected onto the viewport
grid_settings = session.grid_settings = json.load(open(config['CSPY_SETTINGS_FILE']))
nrows = grid_settings['nrows']
ncols = grid_settings['ncols']
grid_1 = session.grid_1 = grid.Grid(
    canvas_size, ncols, nrows, [
        [config['GRID_1_X1'], config['GRID_1_Y1']],
        [config['GRID_1_X1'], config['GRID_1_Y2']],
        [config['GRID_1_X2'], config['GRID_1_Y2']],
        [config['GRID_1_X2'], config['GRID_1_Y1']]],
        viewport, ['slider0'])
grid_2 = session.grid_2 = grid.Grid(
    canvas_size, ncols, nrows, [[0, 0], [0, 100], [50, 100], [50, 0]], viewport)

show_polygons = True
show_basemap = False
show_grid = False
show_typologiezonen = True
show_nahwaermenetz = True

# initialize slider:
slider = session.slider = Slider(canvas_size, grid_1, [0, 100, 50, 150])

# Load data
buildings = gis.read_shapefile(
    config['BUILDINGS_OSM_FILE'], columns={'osm_id': 'int64'}).set_index('osm_id')

buildings = session.buildings = stats.append_csv(config['BUILDINGS_DATA_FILE'], buildings, {
    'Wärmeverbrauch 2017 [kWh]': 'float32',
    'Stromverbrauch 2017 [kWh]': 'float32',
    'Straße' : 'string',
    'Hausnr.': 'string',
})

# data normalized by max values
buildings['waerme_2017_rel'] = buildings['Wärmeverbrauch 2017 [kWh]'] / \
    buildings.max()['Wärmeverbrauch 2017 [kWh]']
buildings['strom_2017_rel'] = buildings['Stromverbrauch 2017 [kWh]'] / \
    buildings.max()['Stromverbrauch 2017 [kWh]']
buildings['adresse'] = buildings['Straße'] + ' ' + buildings['Hausnr.']

# technical data
buildings['CO2'] = [0.5 * random.random() for row in buildings.values]
buildings['investment'] = [random.randint(0,4) for row in buildings.values]

versorgungsarten = ['konventionell', 'medium', 'gruen']
buildings['versorgung'] = [versorgungsarten[random.randint(0,2)] for row in buildings.values]
buildings['anschluss'] = [0 for row in buildings.values]

# psychological data
buildings['EEH'] = [random.random() for row in buildings.values]

# buildings interaction
buildings['cell'] = ""
buildings['selected'] = False

# GIS layers
typologiezonen = gis.read_shapefile(config['TYPOLOGIEZONEN_FILE'])
nahwaermenetz = gis.read_shapefile(config['NAHWAERMENETZ_FILE'])
waermezentrale = gis.read_shapefile(config['WAERMESPEICHER_FILE'], 'Wärmespeicher').append(
    gis.read_shapefile(config['HEIZZENTRALE_FILE']))

# mask viewport with black surface
mask_points = [[0, 0], [100, 0], [100, 100], [0, 100], [0, -50],
               [-50, -50], [-50, 200], [200, 200], [200, -50], [0, -50]]

# UDP server for incoming cspy messages
for grid_, grid_udp in [[grid_1, grid_udp_1], [grid_2, grid_udp_2]]:
    udp_server = udp.UDPServer(*grid_udp, 4096)
    udp_thread = threading.Thread(target=udp_server.listen,
                                  args=(grid_.read_scanner_data,),
                                  daemon=True)
    udp_thread.start()

# stats viz communication
_stats = stats.Stats(stats_io)

print(buildings)

handlers = {
    'calibrate': CalibrationMode(),
    'edit': EditMode(),
    'tui': TuiMode(),
    'simulation': SimulationMode()
}
active_handler = handlers['tui']

############################ Begin Game Loop ##########################
while True:
    # process mouse/keyboard events
    for event in pygame.event.get():
        if active_handler:
            active_handler.process_event(event, config)

        if event.type == KEYDOWN:
            # toggle polygons:
            if event.key == K_p:
                show_polygons = event.key == K_p and not show_polygons
            # toggle basemap:
            if event.key == K_m:
                show_basemap = event.key == K_m and not show_basemap
            # toggle grid:
            elif event.key == K_g:
                show_grid = not show_grid
            # activate tui_mode:
            if event.key == K_t:
                active_handler = handlers['tui']
            # toggle nahwaermenetz:
            if event.key == K_n:
                show_nahwaermenetz = not show_nahwaermenetz
            # toggle calibration:
            elif event.key == K_c:
                active_handler = handlers[
                    'calibrate' if active_handler != handlers['calibrate'] else 'tui']
            # toggle edit-mode to move polygons:
            elif event.key == K_e:
                active_handler = handlers['edit' if active_handler != handlers['edit'] else 'tui']
            # toggle simulation_mode:
            elif event.key == K_s:
                active_handler = handlers[
                    'simulation' if active_handler != handlers['simulation'] else 'tui']
                active_handler = handlers['simulation']
            elif event.key == K_PLUS:
                if session.grid_1.sliders['slider0'] is not None:
                    session.grid_1.sliders['slider0'] += 0.1
                    session.print_verbose(("slider0 =", session.grid_1.sliders['slider0']))
                else:
                    session.grid_1.sliders['slider0'] = 0.1
            elif event.key == K_MINUS:
                if session.grid_1.sliders['slider0'] is not None:
                    session.grid_1.sliders['slider0'] -= 0.1
                    session.print_verbose(("slider0 =", session.grid_1.sliders['slider0']))
                else:
                    session.grid_1.sliders['slider0'] = 0.1
            elif event.key == K_v:
                session.verbose = not session.verbose

        elif event.type == QUIT:
            pygame.quit()
            sys.exit()

    # if active_handler != handlers['calibrate'] and active_handler != handlers['edit']:
    active_handler.update()

    # clear surfaces
    canvas.fill(0)
    viewport.fill(0)
    _gis.surface.fill(0)
    grid_1.surface.fill(0)
    grid_2.surface.fill(0)
    slider.surface.fill(0)

    if show_typologiezonen:
        session.gis.draw_polygon_layer(canvas, typologiezonen, 0, (123, 201, 230, 50))
    session.gis.draw_linestring_layer(canvas, nahwaermenetz, (217, 9, 9), 3)
    session.gis.draw_polygon_layer(canvas, waermezentrale, 0, (252, 137, 0))
    session.gis.draw_polygon_layer(
        canvas, buildings, 0, (96, 205, 21), (213, 50, 21), 'waerme_2017_rel')  # fill and lerp
    # session.gis.draw_polygon_layer(
    #     canvas, buildings, 0, (96, 205, 21), (96, 205, 21), 'waerme_2017_rel')  # fill all equally
    session.gis.draw_polygon_layer(
        canvas, buildings, 1, (0, 0, 0), (0, 0, 0), 'waerme_2017_rel')  # stroke simple black

    # draw grid
    if active_handler != handlers['simulation']:
        grid_1.draw(canvas, show_grid)
        grid_2.draw(canvas, show_grid)

    # draw mask
    pygame.draw.polygon(viewport, (0, 0, 0), viewport.transform(mask_points))

    # draw extras
    if active_handler:
        active_handler.draw(canvas)

    # build clusters of selected buildings and send JSON message
    # clusters = stats.make_clusters(buildings[buildings.selected])
    _stats.send_simplified_dataframe_withenvironment_variables(buildings[buildings.selected], session.environment)

    # render surfaces
    if show_basemap:
        crop_width = 4644
        crop_height = 620
        canvas.blit(basemap.image, (0, 0), (0, 0, crop_width, crop_height))

    # GIS layer
    if show_polygons:
        canvas.blit(_gis.surface, (0, 0))

    # slider
    if active_handler != handlers['simulation']:
        slider.render()
        canvas.blit(slider.surface, (0,0))

    # draw grid
    canvas.blit(grid_1.surface, (0, 0))
    canvas.blit(grid_2.surface, (0, 0))

    canvas.blit(viewport, (0, 0))

    ############ render everything beyond/on top of canvas: ###########

    # mouse position
    if session.verbose:
        font = pygame.font.SysFont('Arial', 20)
        mouse_pos = pygame.mouse.get_pos()
        canvas.blit(font.render(str(mouse_pos), True, (255,255,255)), (300,800))

    pygame.display.update()

    clock.tick(FPS)

    session.ticks_elapsed = (session.ticks_elapsed + 1)
    session.seconds_elapsed = int(session.ticks_elapsed / 12)
