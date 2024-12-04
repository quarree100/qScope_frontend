import pygame
import q100viz.session as session
from q100viz.graphics.colors import colors
from q100viz.settings.config import config
from q100viz.interaction.Slider import Slider


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
        line_height = 50

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
            pygame.Color(222, 222, 222),
            self.slider.bounding_box,
                border_radius=int(self.slider.bounding_box.height/2)            
        )

        # draw horizontal line
        pygame.draw.line(
            canvas,
            pygame.Color(10, 10, 240),
            (self.slider.bounding_box.left, self.slider.value *
             self.slider.bounding_box.height + self.slider.bounding_box.top),
            (self.slider.bounding_box.right, self.slider.value *
             self.slider.bounding_box.height + self.slider.bounding_box.top),
            4
        )

        # slider annotations
        font.set_bold(False)
        text = font.render(str(session.environment['scenario_num_connections']), True, (255, 255, 255))        
        canvas.blit(
            text, 
            text.get_rect(left=self.slider.bounding_box.right, centery=self.slider.bounding_box.top + self.slider.bounding_box.height * self.slider.value)
            )

        text = font.render("0", True, (255, 255, 255))
        canvas.blit(
            text, 
            text.get_rect(right=self.slider.bounding_box.left, centery=self.slider.bounding_box.top)
            )
        text = font.render(str(len(session.buildings.df)), True, (255, 255, 255))        
        canvas.blit(
            text,
            text.get_rect(right=self.slider.bounding_box.left, centery=self.slider.bounding_box.bottom)
            )       
                
        # ----------------------- draw mode buttons: -----------------------
        y += (self.slider.bounding_box.height + 2* line_height)
        keys = ['start_buildings_interaction', 'start_simulation','start_individual_data_view', 'start_total_data_view']
        for i, key in enumerate(keys):

            for temp_key in [key, key+'_disabled']:
                session.icons[temp_key].rect = pygame.Rect(
                    0,
                    y,
                    session.icons[temp_key].image.width,
                    session.icons[temp_key].image.height
                )
                session.icons[temp_key].rect.centerx = self.bounding_box.left + self.bounding_box.width / 4
            
            y += line_height + session.icons[key].rect.height

            # define mode enabled or dsiabled:   
            temp_key = key        
            if key == 'start_simulation':
                temp_key = key + '_disabled' if len(session.buildings.df[session.buildings.df['selected']]) <= 0 else key
            elif key in ['start_individual_data_view', 'start_total_data_view']:
                temp_key = key + '_disabled' if session.environment['current_iteration_round'] == 0 or session.active_mode == session.modes['simulation'] else key                
            elif key == 'start_buildings_interaction':
                temp_key = key + '_disabled' if session.active_mode == session.modes['simulation'] else key
                
            # highlight selected:
            if not temp_key[-8:] == 'disabled':
                color = pygame.Color(255, 120, 55) if session.environment['mode'] == session.modes[key[6:]].name else pygame.Color(222, 222, 222, session.global_alpha),
                pygame.draw.rect(
                    surface=canvas,
                    color=color,
                    rect=session.icons[key].rect.scale_by(1.3),
                    border_radius=session.icons[key].rect.width
                )
                            
            canvas.blit(
                session.icons[temp_key].image,
                session.icons[temp_key].rect.topleft
            )
            
            # button names:
            font = pygame.font.SysFont('Arial', 18)            
            text = font.render(
                f"{session.modes_human_readable[key[6:]]}", 
                True, pygame.Color(255, 255, 255)
                )
            
            text_rect = text.get_rect()
            text_rect.centery = session.icons[key].rect.centery
            text_rect.left = session.icons[key].rect.right + 10
            
            canvas.blit(text, text_rect)            
            
            text_rect.bottom = session.icons[key].rect.bottom
            text_rect.left = session.icons[key].rect.right + 10

            # simulation button extra information:            
            if key == 'start_simulation':
                info_string = ""
                if temp_key == 'start_simulation_disabled':
                    info_string = "[Bitte Gebäude auswählen]" 
                elif session.environment['current_iteration_round'] > 0:
                    info_string = session.modes['simulation'].fail_message
                canvas.blit(pygame.font.SysFont('Arial', 14).render(
                info_string, 
                True, pygame.Color(255, 255, 255)
                ), text_rect)
                
        # simulation progress:
        text = pygame.font.SysFont('Arial', 18).render(
            f"Runde {session.environment['current_iteration_round']}\nSimulation: {session.modes['simulation'].progress}", 
            True, pygame.Color(255, 255, 255)
            )
        text_rect = text.get_rect()
        text_rect.centerx = self.bounding_box.centerx
        text_rect.bottom = self.bounding_box.bottom

        canvas.blit(text, text_rect)
        