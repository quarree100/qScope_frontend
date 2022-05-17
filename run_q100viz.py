import sys
import os
import random
import threading
import json
import pandas
import numpy as np
import pygame
import datetime
from pygame.locals import NOFRAME, KEYDOWN, K_b, K_c, K_e, K_g, K_m, K_n, K_p, K_q, K_s, K_t, K_v, K_PLUS, K_MINUS, QUIT

from config import config
import q100viz.keystone as keystone
import q100viz.gis as gis
import q100viz.grid as grid
import q100viz.udp as udp
import q100viz.stats as stats
from q100viz.simulation_start import Simulation
from q100viz.interaction.interface import *
from q100viz.interaction.simulation_mode import SimulationMode
import q100viz.session as session
# Set FPS
FPS = session.FPS = 12

# set window position
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (320,1440)
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,2160)  # projection to the left

# Initialize program
pygame.init()

clock = pygame.time.Clock()

# UDP receive
grid_udp_1 = ('localhost', 5001)
grid_udp_2 = ('localhost', 5000)

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
    print('loading src_points:' , viewport.src_points)
    print('loading dst_points:' , viewport.dst_points)
except Exception:
    print("Failed to open keystone file")
    viewport.src_points = [[0, 0], [0, 100], [100, 100], [100, 0]]
    viewport.dst_points = [[0, 0], [0, canvas_size[1]], [canvas_size[0], canvas_size[1]], [canvas_size[0], 0]]
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
grid_settings = session.grid_settings = json.load(open(config['CSPY_SETTINGS_FILE']))  # TODO: seperate files for the two grids
nrows = grid_settings['nrows']
ncols = grid_settings['ncols']
grid_1 = session.grid_1 = grid.Grid(
    canvas_size, ncols, nrows, [
        [config['GRID_1_X1'], config['GRID_1_Y1']],
        [config['GRID_1_X1'], config['GRID_1_Y2']],
        [config['GRID_1_X2'], config['GRID_1_Y2']],
        [config['GRID_1_X2'], config['GRID_1_Y1']]],
        viewport, config['GRID_1_SETUP_FILE'],
        ['slider0'], [[50, 130], [50, 100], [100, 100], [100, 130]])  # TODO: rename sliders
grid_2 = session.grid_2 = grid.Grid(
    canvas_size, ncols, nrows, [
        [config['GRID_2_X1'], config['GRID_2_Y1']],
        [config['GRID_2_X1'], config['GRID_2_Y2']],
        [config['GRID_2_X2'], config['GRID_2_Y2']],
        [config['GRID_2_X2'], config['GRID_2_Y1']]],
        viewport, config['GRID_2_SETUP_FILE'],
        ['slider0'], [[0, 130], [0, 100], [50, 100], [50, 130]])

session.show_polygons = False
session.show_basemap = False
show_grid = False
show_typologiezonen = True
show_nahwaermenetz = True
display_viewport = True

##################### Load data #####################
session.buildings = pandas.DataFrame()
session.buildings['energy_source'] = None

# Bestand:
bestand = gis.read_shapefile(
    config['GEBAEUDE_BESTAND_FILE'], columns={
        'Kataster_C': 'string',
        'Kataster_S': 'string',
        'Kataster_H': 'string',
        'Kataster13': 'float',
        'Kataster15': 'float',
        'Kataster_E': 'string'}).set_index('Kataster_C')

bestand.index.names = ['id']

bestand['address'] = bestand['Kataster_S'] + ' ' + bestand['Kataster_H']
bestand = bestand.drop('Kataster_S', 1)
bestand = bestand.drop('Kataster_H', 1)
bestand = bestand.rename(columns = {'Kataster13': 'spec_heat_consumption', 'Kataster15': 'spec_power_consumption', 'Kataster_E': 'energy_source'})

# Neubau:
neubau = gis.read_shapefile(
    config['GEBAEUDE_NEUBAU_FILE'], columns={
        'Kataster_C': 'string',
        'Kataster_S': 'string',
        'Kataster13': 'float',
        'Kataster15': 'float'}).set_index('Kataster_C')

neubau.index.names = ['id']

neubau = neubau.rename(columns={'Kataster_S': 'address', 'Kataster13': 'spec_heat_consumption', 'Kataster15': 'spec_power_consumption'})

gis.print_geodataframe(bestand, print_each_column=True)
gis.print_geodataframe(neubau, print_each_column=True)

# merge:
# buildings = session.buildings = pandas.concat([bestand, neubau])
buildings = session.buildings = bestand

# adjust data
buildings['spec_heat_consumption'] = buildings['spec_heat_consumption'].fillna(0).to_numpy()
buildings['spec_power_consumption'] = buildings['spec_power_consumption'].fillna(0).to_numpy()

# generic data
buildings['CO2'] = (buildings['spec_heat_consumption'] + buildings['spec_power_consumption']) / 20000
electricity_supply_types = ['green', 'gray', 'mix']
buildings['electricity_supplier'] = [electricity_supply_types[random.randint(0,2)] for row in buildings.values]
buildings['connection_to_heat_grid'] = buildings['energy_source'].isna().to_numpy()
# buildings['connection_to_heat_grid'] = buildings['']
buildings['refurbished'] = buildings['connection_to_heat_grid']
buildings['environmental_engagement'] = [random.random() for row in buildings.values]

# buildings interaction
buildings['cell'] = ""
buildings['selected'] = False

# GIS layers
typologiezonen = gis.read_shapefile(config['TYPOLOGIEZONEN_FILE'])
nahwaermenetz = gis.read_shapefile(config['NAHWAERMENETZ_FILE'])
waermezentrale = gis.read_shapefile(config['WAERMESPEICHER_FILE'], 'Waermespeicher').append(
    gis.read_shapefile(config['HEIZZENTRALE_FILE']))

# mask viewport with black surface
mask_points = [[0, 0], [100, 0], [100, 82], [0, 82], [0, -50],
               [-50, -50], [-50, 200], [200, 200], [200, -50], [0, -50]]

# UDP server for incoming cspy messages
for grid_, grid_udp in [[grid_1, grid_udp_1], [grid_2, grid_udp_2]]:
    udp_server = udp.UDPServer(*grid_udp, 4096)
    udp_thread = threading.Thread(target=udp_server.listen,
                                  args=(grid_.read_scanner_data,),
                                  daemon=True)
    udp_thread.start()

# stats viz communication
_stats = session.stats = stats.Stats(stats_io)

handlers = session.handlers

mouse_position = MousePosition(canvas_size)

session.active_handler.activate()

############################ Begin Game Loop ##########################
while True:
    # process mouse/keyboard events
    for event in pygame.event.get():
        if session.active_handler:
            session.active_handler.process_event(event)

        if event.type == KEYDOWN:
            ############################# graphics ####################
            # toggle polygons:
            if event.key == K_p:
                session.show_polygons = event.key == K_p and not session.show_polygons
            # toggle basemap:
            if event.key == K_m:
                session.show_basemap = event.key == K_m and not session.show_basemap
            # toggle grid:
            elif event.key == K_g:
                show_grid = not show_grid

            ##################### mode selection ######################
            # activate input_mode:
            if event.key == K_t:
                session.handlers['input_environment'].activate()
            # toggle nahwaermenetz:
            if event.key == K_n:
                show_nahwaermenetz = not show_nahwaermenetz
            elif event.key == K_b:
                display_viewport = not display_viewport
            # toggle calibration:
            elif event.key == K_c:
                session.active_handler = handlers[
                    'calibrate' if session.active_handler != handlers['calibrate'] else 'input_environment']
            # toggle simulation_mode:
            elif event.key == K_s:
                # if session.active_handler == handlers['simulation']:  # leaving simulation mode
                #     session.active_handler = handlers['input_environment']
                # else:  # enter simulation mode
                #     session.handlers['simulation'].activate()
                #     session.handlers['simulation'].start_simulation()

                # provide data:
                outputs = pandas.DataFrame(columns=['id', 'name', 'framerate'])
                outputs.loc[len(outputs)] = ['0', 'neighborhood', '1']
                outputs.loc[len(outputs)] = ['1', 'households_income_bar', '5']

                params = pandas.DataFrame(columns=['scenario', 'type', 'value'])
                params.loc[len(params)] = ['alpha_scenario', 'string', 'Static_mean']
                params.loc[len(params)] = ['carbon_price_scenario', 'string', 'A-Conservative']
                params.loc[len(params)] = ['energy_price_scenario', 'string', 'Prices_Project start']
                params.loc[len(params)] = ['q100_price_opex_scenario', 'string', '12 ct / kWh (static)']
                params.loc[len(params)] = ['q100_price_capex_scenario', 'string', '1 payment']
                params.loc[len(params)] = ['q100_emissions_scenario', 'string', 'Constant_50g / kWh']

                simulation = Simulation(
                    headless_folder = config['GAMA_HEADLESS_FOLDER'],
                    model_file = config['GAMA_MODEL_FILE'],
                    final_step = 200,
                    until = None,
                    experiment_name = "agent_decision_making")

                # compose dataframe to start gama simulation
                outputs = pandas.DataFrame(columns=['id', 'name', 'framerate'])
                outputs.loc[len(outputs)] = ['0', 'neighborhood', '1']
                outputs.loc[len(outputs)] = ['1', 'households_income_bar', '5']

                params = pandas.DataFrame(columns=['scenario', 'type', 'value'])
                params.loc[len(params)] = ['alpha_scenario', 'string', 'Static_mean']
                params.loc[len(params)] = ['carbon_price_scenario', 'string', 'A-Conservative']
                params.loc[len(params)] = ['energy_price_scenario', 'string', 'Prices_Project start']
                params.loc[len(params)] = ['q100_price_opex_scenario', 'string', '12 ct / kWh (static)']
                params.loc[len(params)] = ['q100_price_capex_scenario', 'string', '1 payment']
                params.loc[len(params)] = ['q100_emissions_scenario', 'string', 'Constant_50g / kWh']

                simulation.make_xml(params, outputs)
                simulation.run_script()

            # toggle poll mode:
            elif event.key == K_q:
                session.handlers['questionnaire'].activate()


            ########## manual slider control for test purposes: #######
            elif event.key == K_PLUS:
                for grid in grid_1, grid_2:
                    if grid.slider.value is not None:
                        grid.slider.value += 0.1
                        # grid.slider.value = round(grid.slider.value + 0.1, 3)
                        session.print_verbose(("slider0 =", grid.slider.value))
                    else:
                        grid.slider.value = 0.1
                    grid.slider.update()
            elif event.key == K_MINUS:
                for grid in grid_1, grid_2:
                    if grid.slider.value is not None:
                        grid.slider.value = round(grid.slider.value - 0.1, 3)
                        session.print_verbose(("slider0 =", grid.slider.value))
                    else:
                        grid.slider.value = 0.1
                    grid.slider.update()


            # verbose mode:
            elif event.key == K_v:
                session.verbose = not session.verbose

        elif event.type == QUIT:
            if session.log != "":
                with open("qScope-log_%s.txt" % datetime.datetime.now(), "w") as f:
                    f.write(session.log)
                    f.close()
            pygame.quit()
            sys.exit()

    # update running mode:
    session.active_handler.update()

    ################################## DRAWING ########################
    # clear surfaces
    canvas.fill(0)
    viewport.fill(0)
    _gis.surface.fill(0)
    for grid in (grid_1, grid_2):
        grid.surface.fill(0)
        grid.slider.surface.fill(0)

    # draw GIS layers:
    if show_typologiezonen:
        session.gis.draw_polygon_layer(canvas, typologiezonen, 0, (123, 201, 230, 50))
    session.gis.draw_linestring_layer(canvas, nahwaermenetz, (217, 9, 9), 3)
    session.gis.draw_polygon_layer(canvas, waermezentrale, 0, (252, 137, 0))
    session.gis.draw_polygon_layer(
        canvas, buildings, 0, (96, 205, 21), (213, 50, 21), 'CO2')  # fill and lerp
    # session.gis.draw_polygon_layer(
    #     canvas, buildings, 0, (96, 205, 21), (96, 205, 21), 'CO2')  # fill all equally
    session.gis.draw_polygon_layer(
        canvas, buildings, 1, (0, 0, 0), (0, 0, 0), 'CO2')  # stroke simple black

    # draw grid
    grid_1.draw(show_grid)
    grid_2.draw(show_grid)

    # draw mask
    pygame.draw.polygon(viewport, (0, 0, 0), viewport.transform(mask_points))

    # draw mode-specific surface:
    if session.active_handler:
        session.active_handler.draw(canvas)

    # render surfaces
    if session.show_basemap:
        crop_width = 4644
        crop_height = 800
        canvas.blit(basemap.image, (0, 0), (0, 0, crop_width, crop_height))

    # GIS layer
    if session.show_polygons:
        canvas.blit(_gis.surface, (0, 0))

    ########################## DATA PROCESSING ########################

    # build clusters of selected buildings and send JSON message
    # clusters = stats.make_clusters(buildings[buildings.selected])

    # export canvas every 1s:
    if session.seconds_elapsed % 1 == 0 and session.verbose and session.flag_export_canvas:
        # create a cropped output canvas and export:
        temp = pygame.Surface((1400, 630))
        temp.blit(canvas, (0,0))
        temp = pygame.transform.rotate(temp, 270)
        pygame.image.save(temp, '../data/canvas.png')
        session.flag_export_canvas = False

    # slider
    for grid in grid_1, grid_2:
        grid_1.slider.render(viewport)
        grid_2.slider.render(viewport)
    # mode_selector.render(viewport)

    # draw grid
    canvas.blit(grid_1.surface, (0, 0))
    canvas.blit(grid_2.surface, (0, 0))

    if display_viewport:
        canvas.blit(viewport, (0, 0))

    ############ render everything beyond/on top of canvas: ###########

    # mouse position
    if session.verbose:
        font = pygame.font.SysFont('Arial', 20)
        mouse_pos = pygame.mouse.get_pos()
        canvas.blit(font.render(str(mouse_pos), True, (255,255,255)), (200,700))
        canvas.blit(font.render(str(grid_1.slider.value), True, (255,255,255)), (800,670))
        canvas.blit(font.render(str(grid_2.slider.value), True, (255,255,255)), (1150,670))

    ############################# pygame time #########################

    pygame.display.update()

    clock.tick(FPS)

    session.ticks_elapsed = (session.ticks_elapsed + 1)
    session.seconds_elapsed = int(session.ticks_elapsed / 12)
