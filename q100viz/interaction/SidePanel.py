import pygame
import numpy as np
import q100viz.session as session
import q100viz.graphics.colors as colors
import q100viz.graphics.graphictools as graphictools
from q100viz.settings.config import config
from q100viz.interaction.Slider import Slider
import q100viz.interaction.PopupUI as ui

class SidePanel:
    def __init__(self, right):
        self.x = right  # position of side panel
        self.bounding_box = pygame.Rect(
            right, 0,
            config['CANVAS_SIZE'][0] - right,
            config['CANVAS_SIZE'][1]
        )

        self.slider = Slider(None)
        self.slider.handle = 'global_connections'
        self.icons = {
            'start_simulation': graphictools.Icon("images/start_simulation.png"),
            'start_simulation_disabled': graphictools.Icon("images/start_simulation_disabled.png"),
            'start_buildings_interaction': graphictools.Icon("images/start_buildings_interaction.png"),
            'start_buildings_interaction_disabled': graphictools.Icon("images/start_buildings_interaction_disabled.png"),
            'start_individual_data_view': graphictools.Icon("images/start_individual_data_view.png"),
            'start_individual_data_view_disabled': graphictools.Icon("images/start_individual_data_view_disabled.png"),
            'start_total_data_view': graphictools.Icon("images/start_total_data_view.png"),
            'start_total_data_view_disabled': graphictools.Icon("images/start_total_data_view_disabled.png"),
            'refurbished': graphictools.Icon("images/refurbished.png"),
            'connection_to_heat_grid': graphictools.Icon("images/connection_to_heat_grid.png"),
            'save_energy': graphictools.Icon("images/save_energy.png"),
        }
        
        for icon in self.icons.values():
            icon.image = pygame.transform.scale(icon.image, (self.bounding_box.width * 0.28, self.bounding_box.width * 0.28))
        
        for key in session.VALID_DECISION_HANDLES:
            self.icons[key].image = pygame.transform.scale(self.icons[key].image, (25, 25))        
        # self.surface = pygame.Surface(
        #     (self.bounding_box.width,
        #     self.bounding_box.height)
        #     )

    def draw(self, canvas):

        # ------------draw bounding box: ------------
        pygame.draw.rect(
            surface=canvas,
            color=pygame.Color(0, 0, 0),
            rect=self.bounding_box
        )

        # ------------------------- TEXT DISPLAY ----------------------

        # global settings:
        font = pygame.font.SysFont('Arial', 24)
        font.set_bold(True)

        y = config["CANVAS_SIZE"][1] * 0.1
        line_height = 60

        text = font.render(f"Netzanschlüsse: {session.environment['scenario_num_connections']}", True,
                           pygame.Color(255, 255, 255))

        canvas.blit(text, text.get_rect(center=(self.bounding_box.centerx, y)))

        # -------------------------- Slider: --------------------------
        y += line_height
        self.slider.bounding_box = pygame.Rect(
            self.bounding_box.left + self.bounding_box.width / 3,
            y,
            self.bounding_box.width / 3,
            self.bounding_box.height / 3
        )

        pygame.draw.rect(
            canvas,
            pygame.Color(222, 222, 222, session.global_alpha),
            self.slider.bounding_box,
                border_radius=int(self.slider.bounding_box.height/2)            
        )

        # draw horizontal slider line
        pygame.draw.line(
            canvas,
            pygame.Color(session.quarree_colors_8bit[2]),
            (self.slider.bounding_box.left -10, self.slider.value *
             self.slider.bounding_box.height + self.slider.bounding_box.top),
            (self.slider.bounding_box.right + 10, self.slider.value *
             self.slider.bounding_box.height + self.slider.bounding_box.top),
            4
        )

        # slider annotations
        font.set_bold(False)
        text = font.render(str(session.environment['scenario_num_connections']), True, (255, 255, 255))
        if session.environment['scenario_num_connections'] > 0 and session.environment['scenario_num_connections'] < len(session.buildings.df) - 1:
            canvas.blit(
                text, 
                text.get_rect(right=self.slider.bounding_box.left - 10, centery=self.slider.bounding_box.top + self.slider.bounding_box.height * self.slider.value)
                )

        text = font.render("0", True, (255, 255, 255))
        canvas.blit(
            text, 
            text.get_rect(right=self.slider.bounding_box.left - 10, centery=self.slider.bounding_box.top)
            )
        text = font.render(str(len(session.buildings.df)), True, (255, 255, 255))        
        canvas.blit(
            text,
            text.get_rect(right=self.slider.bounding_box.left - 10, centery=self.slider.bounding_box.bottom)
            )       
                
        # ----------------------- draw mode buttons: -----------------------
        y += (self.slider.bounding_box.height + 2* line_height)
        keys = ['start_buildings_interaction', 'start_simulation','start_individual_data_view', 'start_total_data_view']
        for key in keys:

            # place icons:
            for temp_key in [key, key+'_disabled']:
                self.icons[temp_key].rect = pygame.Rect(
                    0, y,
                    self.icons[temp_key].image.width,
                    self.icons[temp_key].image.height
                )
                self.icons[temp_key].rect.centerx = self.bounding_box.left + self.bounding_box.width * 0.33
            
            y += line_height + self.icons[key].rect.height

            # define mode enabled or dsiabled:   
            temp_key = key
            if key == 'start_simulation':
                temp_key = key + '_disabled' if len(session.buildings.df[session.buildings.df['selected']]) <= 0 else key
            elif key in ['start_individual_data_view', 'start_total_data_view']:
                temp_key = key + '_disabled' if session.environment['current_iteration_round'] == 0 or session.modes['simulation'].running else key                
            elif key == 'start_buildings_interaction':
                temp_key = key + '_disabled' if session.active_mode == session.modes['simulation'] else key
                
            # highlight selected / interactive:
            if not temp_key[-8:] == 'disabled':
                color = pygame.Color(255, 120, 55) if session.environment['mode'] == session.modes[key[6:]].name else pygame.Color(222, 222, 222, session.global_alpha),
                pygame.draw.rect(
                    surface=canvas,
                    color=color,
                    rect=self.icons[key].rect.scale_by(1.3),
                    border_radius=self.icons[key].rect.width
                )
                            
            canvas.blit(
                self.icons[temp_key].image,
                self.icons[temp_key].rect.topleft
            )
            
            # button names:
            font = pygame.font.SysFont('Arial', 24)            
            text = font.render(
                f"{session.modes_human_readable[key[6:]]}", 
                True, pygame.Color(255, 255, 255)
                )
            
            text_rect = text.get_rect()
            text_rect.centery = self.icons[key].rect.centery
            text_rect.left = self.icons[key].rect.right + self.icons[key].image.width * 0.2
            
            canvas.blit(text, text_rect)            
            
            text_rect.bottom = self.icons[key].rect.bottom
            text_rect.left = self.icons[key].rect.right + self.icons[key].image.width * 0.2

            # simulation button extra information:            
            if key == 'start_simulation':
                info_string = ""
                if temp_key == 'start_simulation_disabled':
                    info_string = "[Bitte Gebäude auswählen]" 
                elif session.environment['current_iteration_round'] > 0:
                    info_string = session.modes['simulation'].fail_message
                canvas.blit(pygame.font.SysFont('Arial', 20).render(
                    info_string, 
                    True, pygame.Color(255, 255, 255)
                ), text_rect)      
                          
        if session.active_mode == session.modes['individual_data_view']:
            ui.select_user(canvas, self.icons)

        # round and simulation progress:
        text = pygame.font.SysFont('Arial', 24).render(
            f"Runde {session.environment['current_iteration_round']}", 
            True, pygame.Color(255, 255, 255)
            )

        canvas.blit(
            text, text.get_rect(centerx = self.bounding_box.centerx, bottom = self.bounding_box.bottom - line_height)
        )

        if session.modes['simulation'].running:
            text = pygame.font.SysFont('Arial', 24).render(
                f"Simulation: {session.modes['simulation'].progress}", 
                True, pygame.Color(255, 255, 255)
                )

            canvas.blit(
                text, text.get_rect(centerx = self.bounding_box.centerx, bottom = self.bounding_box.bottom - 2 * line_height)
            )        

    def handle_mouse_motion(self, pos):        
        if self.slider.bounding_box.collidepoint(pos):
            self.slider.update_from_interaction(pos)
            self.slider.process_value()
            
        if session.modes['simulation'].running: return
        for key in ['start_simulation', 'start_buildings_interaction', 'start_individual_data_view', 'start_total_data_view']:
            rect = self.icons[key].rect
            if rect.collidepoint(pos):
                if session.active_mode == session.modes[key[6:]]: return
                
                if key == 'start_simulation':
                    if (len(session.buildings.df[session.buildings.df['selected']]) <= 0 or len(session.buildings.df[session.buildings.df['selected']]) == 0): return
                elif key in ['start_individual_data_view', 'start_total_data_view']:
                    if session.environment['current_iteration_round'] == 0: return
                
                session.active_mode = session.modes[key[6:]]
                
                if session.active_mode is session.modes['simulation']:
                    session.modes['simulation'].setup()
                    try:
                        pass
                    except Exception as e:
                        print("cannot initialize simulation", e)
        
    def handle_mouse_up(self, pos):
        pass
    
    def process_rotation(self, pos, rotation):
        if self.icons['start_individual_data_view'].rect.collidepoint(pos):
            self.icons['start_individual_data_view'].magnitude = rotation / 360
            session.environment['active_user_focus_data'] = int(rotation / 360 * session.num_of_users)
