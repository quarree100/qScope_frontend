import sys
import os
import threading
import datetime
import shutil
import cProfile

import pygame
import pygame.locals

import q100viz.udp as udp
import q100viz.session as session
from q100viz.settings.config import config
from q100viz.interaction.SidePanel import SidePanel
from q100viz.devtools import devtools as devtools
from q100viz.graphics.graphictools import Icon
from infoscreen.server import init_server
import infoscreen.api as api


class Frontend:
    ############################## PYGAME SETUP ###########################
    def __init__(self, run_in_main_window=False):
        self.FPS = session.FPS = 12  # framerate

        # window position (must be set before pygame.init!)
        if not run_in_main_window:
            os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (
                2000, 2560)  # projection to the right

        # Initialize program
        pygame.init()
        if not devtools.VERBOSE_MODE:
            pygame.mouse.set_visible(False)

        self.clock = pygame.time.Clock()

        ######################### pygame canvas #######################
        # window size:
        canvas_size = session.config['CANVAS_SIZE']
        self.canvas = pygame.display.set_mode(canvas_size, pygame.locals.NOFRAME)
        pygame.display.set_caption("q100viz")

        self.show_nahwaermenetz = True  # display heat grid as red lines
        # displays the area that is being drawn on. used for debugging
        self.display_viewport = True
        self.side_panel = SidePanel(config["CANVAS_SIZE"][0] * 0.855)

        # mask viewport with black surface
        self.mask_points = [
            [0, 0], [85.5, 0],
            [85.5, 82], [0, 82],
            [0, -50], [-50, -50],
            [-50, 200], [200, 200],
            [200, -50], [0, -50]]

        ############# UDP server for incoming gama messages ###########
        # UDP receive
        self.udp_gama = ('localhost', config['UDP_SERVER_PORT'])

        # receive and forward GAMA messages during simulation:
        udp_server = udp.UDPServer(
            'localhost', config['UDP_SERVER_PORT'], 4096)
        udp_thread = threading.Thread(target=udp_server.listen,
                                      args=(session.api.forward_gama_message,),
                                      daemon=True)
        udp_thread.start()
        
        session.icons = {
            'start_simulation': Icon("images/start_simulation.png"),
            'start_buildings_interaction': Icon("images/start_buildings_interaction.png"),
            'start_individual_data_view': Icon("images/start_individual_data_view.png"),
            'start_total_data_view': Icon("images/start_total_data_view.png"),
            'refurbished': Icon("images/refurbished.png"),
            'connection_to_heat_grid': Icon("images/connection_to_heat_grid.png"),
            'save_energy': Icon("images/save_energy.png"),
        }
        
        for key in session.VALID_DECISION_HANDLES:
            session.icons[key].image = pygame.transform.scale(session.icons[key].image, (25, 25))
        
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
            session.active_mode.process_event(event)
                
            if event.type == pygame.locals.MOUSEMOTION:
                self.handle_mouse_motion()

            elif event.type == pygame.locals.MOUSEBUTTONDOWN:
                self.handle_mouse_down(event)

            elif event.type == pygame.locals.MOUSEBUTTONUP:
                self.handle_mouse_up(pygame.mouse.get_pos())
            
            elif event.type == pygame.locals.KEYDOWN:
                ############################# graphics ####################
                # toggle polygons:
                if event.key == pygame.locals.K_p:
                    session.show_polygons = event.key == pygame.locals.K_p and not session.show_polygons
                # toggle basemap:
                if event.key == pygame.locals.K_m:
                    session.show_basemap = event.key == pygame.locals.K_m and not session.show_basemap
                # toggle nahwaermenetz:
                elif event.key == pygame.locals.K_n:
                    self.show_nahwaermenetz = not self.show_nahwaermenetz
                elif event.key == pygame.locals.K_b:
                    self.display_viewport = not self.display_viewport

                ##################### mode selection ######################
                elif event.key == pygame.locals.K_0:
                    session.active_mode = session.buildings_interaction
                # enter simulation mode:
                elif event.key == pygame.locals.K_9:
                    session.modes['simulation'].setup()
                    session.active_mode = session.modes['simulation']
                elif event.key == pygame.locals.K_8:
                    session.active_mode = session.individual_data_view
                elif event.key == pygame.locals.K_7:
                    session.active_mode = session.total_data_view

                # verbose mode:
                elif event.key == pygame.locals.K_v:
                    devtools.VERBOSE_MODE = not devtools.VERBOSE_MODE

            elif event.type == pygame.locals.QUIT:
                print("-" * 72)
                print("Closing application.")
                if devtools.log != "":
                    print("Full log exported to qScope-log_%s.txt" %
                          str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")))
                    with open(session.modes['simulation'].output_folder + "/qScope-log_%s.txt" % str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")), "w") as f:
                        f.write(devtools.log)
                        f.close()
                if devtools.test_run:
                    try:
                        shutil.rmtree(session.modes['simulation'].output_folder)
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
        
        # draw mask
        mask_color = (0, 0, 0) if not session.flag_mockup_mode else (
            128, 128, 128)
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
        # try:
        session.active_mode.draw(session.viewport)
        # except Exception as e:
        #     print(f"{session.active_mode.name} cannot draw frontend:", e)
        #     devtools.log += "\nCannot draw frontend: %s" % e
            
        self.side_panel.draw(session.viewport)

        # basemap
        if session.show_basemap:
            crop_width = self.canvas.get_width(
            ) * self.mask_points[1][0] / 100  # 4644
            crop_height = self.canvas.get_height(
            ) * self.mask_points[2][1] / 100  # 800
            self.canvas.blit(session.basemap.image, (0, 0),
                             (0, 0, crop_width, crop_height))

        if session.show_polygons:
            self.canvas.blit(session._gis.surface, (0, 0))            

        ########################## DATA PROCESSING ########################

        if self.display_viewport:
            self.canvas.blit(session.viewport, (0, 0))

        ############ render everything beyond/on top of canvas: ###########

        ############################# pygame time #########################

        pygame.display.update()

        self.clock.tick(self.FPS)

    def handle_mouse_down(self, event):
        pass
                    
                                
    def handle_mouse_motion(self):
        mouse_pos = pygame.mouse.get_pos()
        for popup in session.popup_menus.values():
            if popup.dragging:
                # move the boxes:
                for b, box in enumerate(popup.boxes):
                    box.left = mouse_pos[0] - popup.drag_offset[b][0]
                    box.top = mouse_pos[1] - popup.drag_offset[b][1]
                return
            elif popup.bounding_box.collidepoint(mouse_pos):
                popup.handle_mouse_motion(mouse_pos)
                return
            
        if self.side_panel.slider.bounding_box.collidepoint(mouse_pos):
            self.side_panel.slider.update_from_interaction(mouse_pos)
            self.side_panel.slider.process_value()
        
    def handle_mouse_up(self, mouse_pos):
        for popup in session.popup_menus.values():
            popup.dragging = False
           
        for key in ['start_simulation', 'start_buildings_interaction', 'start_individual_data_view', 'start_total_data_view']:
            rect = session.icons[key].rect
            if rect.collidepoint(mouse_pos):
                session.active_mode = session.modes[key[6:]]
                if session.active_mode is session.modes['simulation']:
                    session.modes['simulation'].setup()
            
        session.api.send_dict(session.environment)
        session.api.send_message_as_json(session.buildings.get_dict_with_api_wrapper())
            
            