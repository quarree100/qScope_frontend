import pygame
import q100viz.session as session
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
        y = self.bounding_box.height * 3/4
        image_width = session.icons['start_buildings_interaction'].image.width
        x = self.bounding_box.left + 0.25 * image_width
        for i, key in enumerate(['start_buildings_interaction', 'start_individual_data_view', 'start_total_data_view']):

            session.icons[key].rect = pygame.Rect(
                x + i * self.bounding_box.width / 3,
                y,
                session.icons[key].image.width,
                session.icons[key].image.height
            )
            
            # highlight selected:
            if session.environment['mode'] == session.modes[key[6:]].name:
                pygame.draw.rect(
                    surface=canvas,
                    color=pygame.Color(255, 120, 55, session.global_alpha),
                    rect=session.icons[key].rect.scale_by(1.3),
                    border_radius=session.icons[key].rect.width
                )
            
            canvas.blit(
                session.icons[key].image,
                session.icons[key].rect.topleft
            )
            
        # simulation button:
        y += 2 * line_height

        if session.environment['mode'] == 'simulation':
            pygame.draw.rect(
                surface=canvas,
                color=pygame.Color(255, 120, 55, session.global_alpha),
                rect=session.icons['start_simulation'].rect
            )

        
        session.icons['start_simulation'].rect = pygame.Rect(
            self.bounding_box.centerx - 0.5 * session.icons['start_simulation'].image.width,
            y,
            session.icons['start_simulation'].image.width,
            session.icons['start_simulation'].image.height
        )
            
        canvas.blit(
            session.icons['start_simulation'].image,
            session.icons['start_simulation'].rect.topleft,
        )            