import sys
import os
import threading
import datetime

import pygame
from pygame.locals import NOFRAME, KEYDOWN, K_3, K_4, K_5, K_6, K_b, K_c, K_g, K_m, K_n, K_p, K_v, K_PLUS, K_MINUS, QUIT

import q100viz.udp as udp
import q100viz.session as session
from q100viz.settings.config import config
from q100viz.interaction.interface import *

class Frontend:
############################## PYGAME SETUP ###########################
    def __init__(self, run_in_main_window=False):
        self.FPS = session.FPS = 12 # framerate

        # set window position
        if not run_in_main_window:
            os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (
                0, 2560)  # projection to the left

        # Initialize program
        pygame.init()

        self.clock = pygame.time.Clock()

        # UDP receive
        grid_udp_1 = ('localhost', 5001)
        grid_udp_2 = ('localhost', 5000)
        self.udp_gama = ('localhost', 8081)

        # Set up display
        canvas_size = session.config['CANVAS_SIZE']
        self.canvas = pygame.display.set_mode(canvas_size, NOFRAME)
        pygame.display.set_caption("q100viz")

        self.show_grid = False  # draws a representation of the physical grid of tiles onto the canvas
        self.show_typologiezonen = False  # deprecated. shows specific polygons, if enabled.
        self.show_nahwaermenetz = True  # display heat grid as red lines
        self.display_viewport = True  # displays the area that is being drawn on. used for debugging

        ################### mask viewport with black surface ##################
        self.mask_points = [[0, 0], [85.5, 0], [85.5, 82], [0, 82], [0, -50],
                    [-50, -50], [-50, 200], [200, 200], [200, -50], [0, -50]]

        ################# UDP server for incoming cspy messages ###############
        for grid_, grid_udp in [[session.grid_1, grid_udp_1], [session.grid_2, grid_udp_2]]:
            udp_server = udp.UDPServer(*grid_udp, 4096)
            udp_thread = threading.Thread(target=udp_server.listen,
                                        args=(grid_.read_scanner_data,),
                                        daemon=True)
            udp_thread.start()

        # receive and forward GAMA messages during simulation:
        udp_server = udp.UDPServer('localhost', config['UDP_SERVER_PORT'], 4096)
        udp_thread = threading.Thread(target=udp_server.listen,
                                    args=(session.api.forward_gama_message,),
                                    daemon=True)
        udp_thread.start()


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

                ##################### mode selection ######################
                # enter questionnaire mode:
                # if event.key == K_1:
                #     session.active_mode = session.questionnaire
                # activate Input Scenarios Mode:
                # elif event.key == K_2:
                    # session.active_mode = session.input_scenarios
                # activate Input Households Mode:
                elif event.key == K_3:
                    session.active_mode = session.buildings_interaction
                # enter simulation mode:
                elif event.key == K_4:
                    session.environment['active_scenario_handle'] = 'A'
                    session.simulation.setup()
                    session.active_mode = session.simulation
                elif event.key == K_5:
                    session.active_mode = session.individual_data_view
                elif event.key == K_6:
                    session.active_mode = session.total_data_view

                # toggle calibration:
                elif event.key == K_c:
                    session.active_mode = session.calibration if session.active_mode != session.calibration else session.buildings_interaction

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
                    session.VERBOSE_MODE = not session.VERBOSE_MODE

            elif event.type == QUIT:
                if session.log != "":
                    with open("qScope-log_%s.txt" % datetime.datetime.now(), "w") as f:
                        f.write(session.log)
                        f.close()
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
        if self.show_typologiezonen:
            session._gis.draw_polygon_layer(
                self.canvas, session._gis.typologiezonen, 0, (123, 201, 230, 50))
        if session.show_polygons:
            session._gis.draw_linestring_layer(
                self.canvas, session._gis.nahwaermenetz, (217, 9, 9), 3)
            # session._gis.draw_polygon_layer(
                # canvas, session._gis.waermezentrale, 0, (252, 137, 0))
            session._gis.draw_buildings_connections(
                session.buildings.df)  # draw lines to closest heat grid
            if session.VERBOSE_MODE:
                session._gis.draw_polygon_layer_float(
                    self.canvas, session.buildings.df, 0, (96, 205, 21), (213, 50, 21), 'spec_heat_consumption')  # fill and lerp
            else:
                session._gis.draw_polygon_layer_bool(
                    self.canvas, session.buildings.df, 0, (213, 50, 21), (96, 205, 21), 'connection_to_heat_grid')  # fill and lerp
            session._gis.draw_polygon_layer_bool(
                self.canvas, session.buildings.df, 1, (0, 0, 0), (0, 0, 0), 'connection_to_heat_grid')  # stroke simple black

            # stroke according to connection status:
            session._gis.draw_polygon_layer_bool(
                surface=self.canvas, df=session.buildings.df, stroke=1, fill_false=(0, 0, 0), fill_true=(0, 168, 78), fill_attr='connection_to_heat_grid')

            # color buildings if connection is not -1:
            # session.gis.draw_polygon_layer_connection_year(
            #     session.buildings.df,
            #     stroke=0,
            #     fill_true=(96, 205, 21),
            #     fill_false=(213, 50, 21),
            #     fill_attr='connection_to_heat_grid')

            # # stroke simple black:
            # session.gis.draw_polygon_layer_bool(
            #     canvas, session.buildings.df, 1, (0, 0, 0), (0, 0, 0), 'connection_to_heat_grid')

            # # stroke according to connection status:
            # session.gis.draw_polygon_layer_connection_year(
            #     session.buildings.df,
            #     stroke=2,
            #     fill_true=(0, 168, 78),
            #     fill_false=(0),
            #     fill_attr='connection_to_heat_grid')

        # draw grid
        session.grid_1.draw(self.show_grid)
        session.grid_2.draw(self.show_grid)

        # draw mask
        pygame.draw.polygon(session.viewport, (0, 0, 0),
                            session.viewport.transform(self.mask_points))

        # draw mode-specific surface:
        if session.active_mode:
            session.active_mode.draw(session.viewport)

        # render surfaces
        if session.show_basemap:
            crop_width = 4644
            crop_height = 800
            self.canvas.blit(session.basemap.image, (0, 0),
                        (0, 0, crop_width, crop_height))

        # GIS layer
        if session.show_polygons:
            self.canvas.blit(session._gis.surface, (0, 0))

        ########################## DATA PROCESSING ########################

        # export canvas:
        # if session.flag_export_canvas:
        #     # create a cropped output canvas and export:
        #     temp = pygame.Surface((1460, 630))
        #     temp.blit(session.gis.surface, (0,0))
        #     temp = pygame.transform.rotate(temp, 270)
        #     pygame.image.save(temp, '../data/canvas.png')
        #     session.flag_export_canvas = False

        # slider
        for grid in session.grid_1, session.grid_2:
            for slider in grid.sliders.values():
                slider.render(session.viewport)
                slider.render(session.viewport)

        # draw grid
        self.canvas.blit(session.grid_1.surface, (0, 0))
        self.canvas.blit(session.grid_2.surface, (0, 0))

        if self.display_viewport:
            self.canvas.blit(session.viewport, (0, 0))

        ############ render everything beyond/on top of canvas: ###########

        font = pygame.font.SysFont('Arial', 20)
        # mouse position
        # if session.VERBOSE_MODE:
        # mouse_pos = pygame.mouse.get_pos()
        # canvas.blit(font.render(str(mouse_pos), True, (255,255,255)), (200,700))

        ############################# pygame time #########################

        pygame.display.update()

        self.clock.tick(self.FPS)

        session.ticks_elapsed = (session.ticks_elapsed + 1)
        session.seconds_elapsed = int(session.ticks_elapsed / 12)
