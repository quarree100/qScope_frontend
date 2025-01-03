import sys
import os
import threading
import datetime
import shutil
import numpy
import cProfile

import pygame
import pygame.locals

from pythontuio import TuioClient

import q100viz.udp as udp
import q100viz.session as session
from q100viz.settings.config import config
from q100viz.interaction.SidePanel import SidePanel
from q100viz.interaction.Tangibles import Tuio_Listener, Tangible
from q100viz.devtools import devtools as devtools
from q100viz.graphics.graphictools import Icon
import infoscreen.api as api


class Frontend:
    ############################## PYGAME SETUP ###########################
    def __init__(self, run_in_main_window=False):
        self.FPS = session.FPS = 20  # framerate

        # window position (must be set before pygame.init!)
        if not run_in_main_window:
            os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (
                0, 1080)  # projection to the right

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
            [85.5, 100], [0, 100],
            [0, -50], [-50, -50],
            [-50, 200], [200, 200],
            [200, -50], [0, -50]]
        if devtools.VERBOSE_MODE:
            self.mask_points = [
            [0, 0], [85.5, 0],
            [85.5, 85], [0, 85],
            [0, -50], [-50, -50],
            [-50, 200], [200, 200],
            [200, -50], [0, -50]] 

        ############# UDP server for incoming gama messages ###########
        # http_thread = threading.Thread(
        #     target=init_server,
        #     args=[config['HTTP_SERVER_PORT'], config['UDP_SERVER_PORT']],
        #     daemon=True)
        # http_thread.start()
        
        io = 'http://localhost:' + str(config['UDP_SERVER_PORT'])  # Socket.io
        session.api = api.API(io)

        # receive and forward GAMA messages during simulation:
        self.udp_gama = ('localhost', config['UDP_SERVER_PORT'])
        udp_server = udp.UDPServer(
            'localhost', config['UDP_SERVER_PORT'], 4096)
        udp_thread = threading.Thread(
            target=udp_server.listen, args=(api.forward_gama_message,),
            daemon=True)
        udp_thread.start()
        
        # tuio:
        tuio_listener = Tuio_Listener()
        
        tuio_client = TuioClient((config['TUIO_ADDRESS'], config['TUIO_PORT']))
        tuio_thread = threading.Thread(target=tuio_client.start, daemon=True)
        tuio_client.add_listener(tuio_listener)
        
        tuio_thread.start()
                
        if devtools.test_run:
            devtools.profiler = cProfile.Profile()
            devtools.profiler.enable()

############################ Begin Game Loop ##########################

    def run(self):

        if session.previous_mode is not session.active_mode:
            session.previous_mode = session.active_mode
            session.active_mode.activate()

        # process mouse/keyboard events
        for event in pygame.event.get():
                
            if event.type == pygame.locals.MOUSEMOTION:
                if not devtools.VERBOSE_MODE: return
                self.handle_mouse_motion(pygame.mouse.get_pos())

            elif event.type == pygame.locals.MOUSEBUTTONDOWN:
                if not devtools.VERBOSE_MODE: return
                self.handle_mouse_down(pygame.mouse.get_pos())

            elif event.type == pygame.locals.MOUSEBUTTONUP:
                if not devtools.VERBOSE_MODE: return
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
                elif event.key == pygame.locals.K_i:
                    print(session.buildings.df.loc[session.buildings.df['selected']])

                # verbose mode:
                elif event.key == pygame.locals.K_v:
                    devtools.VERBOSE_MODE = not devtools.VERBOSE_MODE
                    pygame.mouse.set_visible(devtools.VERBOSE_MODE)
                    self.mask_points = [
                        [0, 0], [85.5, 0],
                        [85.5, 100], [0, 100],
                        [0, -50], [-50, -50],
                        [-50, 200], [200, 200],
                        [200, -50], [0, -50]]
                    if devtools.VERBOSE_MODE:
                        self.mask_points = [
                        [0, 0], [85.5, 0],
                        [85.5, 85], [0, 85],
                        [0, -50], [-50, -50],
                        [-50, 200], [200, 200],
                        [200, -50], [0, -50]]

            elif event.type == pygame.locals.QUIT:
                print("-" * 72)
                print("Closing application.")

                if devtools.test_run:
                    try:
                        shutil.rmtree(session.modes['simulation'].output_folder)
                        print(
                            "data output folder was deleted, because q100viz was run with --test_run flag")
                    except:
                        pass
                    devtools.profiler.disable()
                    devtools.profiler.print_stats(sort='cumulative')

                if devtools.log != "":
                    with open(session.modes['simulation'].output_folder + "/qScope-log_%s.txt" % str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")), "w") as f:
                        f.write(devtools.log)
                        f.close()
                    print("Full log exported to qScope-log_%s.txt" %
                    str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")))
                    
                pygame.quit()
                sys.exit()

        ################################## DRAWING ########################
        # clear surfaces
        self.canvas.fill(0)
        session.viewport.fill(0)
        session._gis.surface.fill(0)
        
        # draw mask
        mask_color = (0, 0, 0) if not session.flag_mockup_mode else (
            128, 128, 128)
        pygame.draw.polygon(
            session.viewport, mask_color,
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
            
        # basemap
        if session.show_basemap:
            crop_width = self.canvas.get_width(
            ) * self.mask_points[1][0] / 100  # 4644
            crop_height = self.canvas.get_height(
            ) * self.mask_points[2][1] / 100  # 800
            self.canvas.blit(session.basemap.image, (0, 0),
                             (0, 0, crop_width, crop_height))

        self.side_panel.draw(session.viewport)

        if session.show_polygons:
            self.canvas.blit(session._gis.surface, (0, 0))
        
        # tangibles destruction:
        for tangible in [t for t in list(session.tangibles.values()) if t]:
            tangible.draw(session.viewport)
            if tangible.destroy_me: 
                tangible.destroy()
                session.popup_menus[tangible.id] = None

        # bottom information area:
        if devtools.VERBOSE_MODE: 
            for tangible in [t for t in list(session.tangibles.values()) if t]:
                tangible.draw_verbose(session.viewport)
                font = pygame.font.SysFont('Arial', 12)
                for a, c in enumerate([pygame.Color(0,0,0), pygame.Color(255, 255, 255)]):
                    for b, l in enumerate([session.tangibles.keys(), session.popup_menus.keys()]):
                        text = font.render(str([f"{k}" for k in l]), False, c)
                        session.viewport.blit(text, (20 + a, self.mask_points[2][1] / 100 * config['CANVAS_SIZE'][1] + a + b * 10))
            # UDP message stack:
            session.viewport.blit(
                pygame.font.SysFont('Arial', 12).render(
                    f"UDP message stack: {len(session.api.message_stack)}", False, pygame.Color(255,255,255), pygame.Color(0, 0, 0)
                ),
                (0, config['CANVAS_SIZE'][1] - 10)
            )
            
            # selected buildings:
            for i, (idx, bd) in enumerate(session.buildings.df.loc[session.buildings.df['selected']].iterrows()):
                for j, key in enumerate(session.COMMUNICATION_RELEVANT_KEYS):
                    session.viewport.blit(
                    pygame.font.SysFont('Arial', 12).render(
                        f"{key}: {bd[key]}", False, pygame.Color(255,255,255), pygame.Color(0, 0, 0)
                    ),
                    (250 + i*300, self.mask_points[2][1] / 100 * config['CANVAS_SIZE'][1] + j*10)
                    )

        
        # popup destruction:
        for popup in [p for p in list(session.popup_menus.values()) if p]:
            if popup.destroy_me: 
                session.popup_menus[popup.tangible_id] = None
                popup.destroy()
        
        if self.display_viewport:
            self.canvas.blit(session.viewport, (0, 0))
           
        ############ render everything beyond/on top of canvas: ###########

        ############################# pygame time #########################

        session.global_alpha = 30 + \
            abs(int(numpy.sin(pygame.time.get_ticks() / 1000) * 105))

        pygame.display.update()

        self.clock.tick(self.FPS)

    def handle_mouse_down(self, pos):
        session.active_mode.process_event(pos)
                    
    def handle_mouse_motion(self, pos):
        for popup in [p for p in list(session.popup_menus.values()) if p]:
            if popup.dragging:
                # move the boxes:
                for b, box in enumerate(popup.boxes):
                    box.left = pos[0] - popup.drag_offset[b][0]
                    box.top = pos[1] - popup.drag_offset[b][1]
                return
            elif popup.bounding_box.collidepoint(pos):
                popup.handle_mouse_motion(pos)
                return
            
        self.side_panel.handle_mouse_motion(pos)
            
    def handle_mouse_up(self, pos):
        for popup in [p for p in list(session.popup_menus.values()) if p]:
            popup.dragging = False
           
        self.side_panel.handle_mouse_up(pos)
            
        session.api.send_dict(session.environment)
        session.api.send_message_as_json(session.buildings.get_dict_with_api_wrapper())