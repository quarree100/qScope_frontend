import sys
import os
import threading
import datetime
import shutil
import cProfile

import pygame
from pygame.locals import NOFRAME, KEYDOWN, K_0, K_9, K_8, K_7, K_b, K_c, K_g, K_m, K_n, K_p, K_v, K_w, K_PLUS, K_MINUS, QUIT

import q100viz.udp as udp
import q100viz.session as session
from q100viz.settings.config import config
from q100viz.interaction.interface import *
from q100viz.devtools import devtools as devtools


class Frontend:
    ############################## PYGAME SETUP ###########################
    def __init__(self, run_in_main_window=False):
        self.FPS = session.FPS = 12  # framerate

        # window position (must be set before pygame.init!)
        if not run_in_main_window:
            os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (
                0, 2560)  # projection to the left

        # Initialize program
        pygame.init()

        self.clock = pygame.time.Clock()

        ######################### pygame canvas #######################
        # window size:
        canvas_size = session.config['CANVAS_SIZE']
        self.canvas = pygame.display.set_mode(canvas_size, NOFRAME)
        pygame.display.set_caption("q100viz")

        # draws a representation of the physical grid of tiles onto the canvas
        self.show_grid = False
        self.show_nahwaermenetz = True  # display heat grid as red lines
        # displays the area that is being drawn on. used for debugging
        self.display_viewport = True

        # mask viewport with black surface
        self.mask_points = [[0, 0], [85.5, 0], [85.5, 82], [0, 82], [0, -50],
                            [-50, -50], [-50, 200], [200, 200], [200, -50], [0, -50]]

        ############# UDP server for incoming cspy messages ###########
        # UDP receive
        grid_udp_1 = ('localhost', config['UDP_TABLE_1'])
        grid_udp_2 = ('localhost', config['UDP_TABLE_2'])
        self.udp_gama = ('localhost', config['UDP_SERVER_PORT'])

        for grid_, grid_udp in [[session.grid_1, grid_udp_1], [session.grid_2, grid_udp_2]]:
            udp_server = udp.UDPServer(*grid_udp, 4096)
            udp_thread = threading.Thread(target=udp_server.listen,
                                          args=(grid_.read_scanner_data,),
                                          daemon=True)
            udp_thread.start()

        # receive and forward GAMA messages during simulation:
        udp_server = udp.UDPServer(
            'localhost', config['UDP_SERVER_PORT'], 4096)
        udp_thread = threading.Thread(target=udp_server.listen,
                                      args=(session.api.forward_gama_message,),
                                      daemon=True)
        udp_thread.start()


        if devtools.test_run:
            devtools.profiler = cProfile.Profile()
            devtools.profiler.enable()
############################ Begin Game Loop ##########################
        
    def run(self):

        if session.previous_mode is not session.active_mode:
            session.active_mode.activate()
            session.previous_mode = session.active_mode

        # process mouse/keyboard events
        for event in pygame.event.get():
            if session.active_mode:
                session.active_mode.process_event(event)

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
                    self.show_grid = not self.show_grid
                # toggle nahwaermenetz:
                elif event.key == K_n:
                    self.show_nahwaermenetz = not self.show_nahwaermenetz
                elif event.key == K_b:
                    self.display_viewport = not self.display_viewport

                elif event.key == K_w:
                    print(
                        session.buildings.df[session.buildings.df['group'] >= 0])

                ##################### mode selection ######################
                # enter questionnaire mode:
                # if event.key == K_1:
                #     session.active_mode = session.questionnaire
                # activate Input Scenarios Mode:
                # elif event.key == K_2:
                    # session.active_mode = session.input_scenarios
                # activate Input Households Mode:
                elif event.key == K_0:
                    session.active_mode = session.buildings_interaction
                # enter simulation mode:
                elif event.key == K_9:
                    session.simulation.setup()
                    session.active_mode = session.simulation
                elif event.key == K_8:
                    session.active_mode = session.individual_data_view
                elif event.key == K_7:
                    session.active_mode = session.total_data_view

                # toggle calibration:
                elif event.key == K_c:
                    if session.active_mode != session.calibration:
                        session.active_mode = session.calibration
                        self.show_grid = True
                    else:
                        session.active_mode = session.buildings_interaction
                        self.show_grid = False

                ########## manual slider control for test purposes: #######
                elif event.key == K_PLUS:
                    for grid in session.grid_1, session.grid_2:
                        for key, val in grid.sliders.items():
                            if grid.sliders[key].value is not None:
                                grid.sliders[key].value += 0.1
                            else:
                                grid.sliders[key].value = 0.1
                            grid.sliders[key].process_value()
                elif event.key == K_MINUS:
                    for grid in session.grid_1, session.grid_2:
                        for key, val in grid.sliders.items():
                            if grid.sliders[key].value is not None:
                                grid.sliders[key].value = round(
                                    grid.sliders[key].value - 0.1, 3)
                            else:
                                grid.sliders[key].value = 0.1
                            grid.sliders[key].process_value()

                # verbose mode:
                elif event.key == K_v:
                    devtools.VERBOSE_MODE = not devtools.VERBOSE_MODE

            elif event.type == QUIT:
                print("-" * 72)
                print("Closing application.")
                if devtools.log != "":
                    print("Full log exported to qScope-log_%s.txt" %
                          str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")))
                    with open(session.simulation.output_folder + "/qScope-log_%s.txt" % str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")), "w") as f:
                        f.write(devtools.log)
                        f.close()
                if devtools.test_run:
                    try:
                        shutil.rmtree(session.simulation.output_folder)
                        print(
                            "data output folder was deleted, because q100viz was run with --test_run flag")
                    except: 
                        pass
                    devtools.profiler.disable()
                    devtools.profiler.print_stats(sort='cumulative')

                pygame.quit()
                sys.exit()

        # update running mode:
        session.active_mode.update()

        ################################## DRAWING ########################
        # clear surfaces
        self.canvas.fill(0)
        session.viewport.fill(0)
        session._gis.surface.fill(0)
        for grid in (session.grid_1, session.grid_2):
            grid.surface.fill(0)
            for slider in grid.sliders.values():
                slider.surface.fill(0)

        # draw GIS layers:
        if session.show_polygons:
            session._gis.draw_linestring_layer(
                self.canvas, session._gis.nahwaermenetz, (217, 9, 9), 3)
            session._gis.draw_buildings_connections(
                session.buildings.df)  # draw lines to closest heat grid

            # fill and lerp:
            if devtools.VERBOSE_MODE:
                session._gis.draw_polygon_layer_float(
                    self.canvas, session.buildings.df, 0,
                    (96, 205, 21),
                    (213, 50, 21),
                    'spec_heat_consumption')
            else:
                session._gis.draw_polygon_layer_bool(
                    self.canvas, session.buildings.df, 0,
                    (213, 50, 21),
                    (96, 205, 21),
                    'connection_to_heat_grid')

            # stroke simple black:
            session._gis.draw_polygon_layer_bool(
                self.canvas, session.buildings.df, 1,
                (0, 0, 0),
                (0, 0, 0),
                'connection_to_heat_grid')

            # stroke according to connection status:
            session._gis.draw_polygon_layer_bool(
                surface=self.canvas, df=session.buildings.df,
                stroke=1,
                fill_false=(0, 0, 0),
                fill_true=(0, 168, 78),
                fill_attr='connection_to_heat_grid')

        # draw grid outline
        session.grid_1.draw(self.show_grid)  # draws polygons to grid.surface
        session.grid_2.draw(self.show_grid)

        # draw mask
        mask_color = (0,0,0) if not session.flag_mockup_mode else (128, 128, 128)
        pygame.draw.polygon(session.viewport, mask_color,
                            session.viewport.transform(self.mask_points))

        if session.flag_mockup_mode:
            font = pygame.font.SysFont("Arial", 40)
            session.viewport.blit(
                font.render(
                    "Running demo mode!",
                    True,
                    pygame.Color(0, 0, 0)),
                    (2, 2)
            )
            session.viewport.blit(
                font.render(
                    "Running demo mode!",
                    True,
                    pygame.Color(255, 255, 255)),
                    (0, 0)
            )
            
        # draw mode-specific surface:
        if session.active_mode:
            session.active_mode.draw(session.viewport)

        # basemap
        if session.show_basemap:
            crop_width = 4644
            crop_height = 800
            self.canvas.blit(session.basemap.image, (0, 0),
                             (0, 0, crop_width, crop_height))

        # render GIS layer
        if session.show_polygons:
            self.canvas.blit(session._gis.surface, (0, 0))

        ########################## DATA PROCESSING ########################

        # slider
        for grid in session.grid_1, session.grid_2:
            for slider in grid.sliders.values():
                slider.draw_controls(session.viewport)

        # draw grid
        self.canvas.blit(session.grid_1.surface, (0, 0))
        self.canvas.blit(session.grid_2.surface, (0, 0))

        if self.display_viewport:
            self.canvas.blit(session.viewport, (0, 0))

        ############ render everything beyond/on top of canvas: ###########

        pass

        ############################# pygame time #########################

        pygame.display.update()

        self.clock.tick(self.FPS)
