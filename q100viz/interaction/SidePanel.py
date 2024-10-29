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
            color=pygame.Color(255, 0, 255, 60),
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

        # Slider:
        y += line_height
        self.slider.bounding_box = pygame.Rect(
                self.bounding_box.left,
                y,
                self.bounding_box.width, 
                self.bounding_box.height / 3
            )
                
        pygame.draw.rect(
            canvas,
            pygame.Color(200, 200, 200),
            self.slider.bounding_box
        )
        
        # draw horizontal line
        pygame.draw.line(
            canvas,
            pygame.Color(10, 10, 240),
            (self.slider.bounding_box.left, self.slider.value * self.slider.bounding_box.height + self.slider.bounding_box.top),
            (self.slider.bounding_box.right, self.slider.value * self.slider.bounding_box.height + self.slider.bounding_box.top), 
            4
        )
        
        y += self.slider.bounding_box.height + text.get_rect().height
        font.set_bold(False)
        text = font.render(
            str(int(self.slider.value * len(session.buildings.df))), 
            True, pygame.Color(255, 255, 255)
            )

        canvas.blit(text, text.get_rect(center=(self.bounding_box.centerx, y)))

        return 
        i += 1
        canvas.blit(font.render(
            "Quartiersdaten", True, pygame.Color(255, 255, 255)), (self.x, y + i * line_height))

        font = pygame.font.SysFont('Arial', 18)
        i += 1
        canvas.blit(font.render(
            "Individualdaten", True, pygame.Color(255, 255, 255)),
            (self.x, y + i * line_height)
        )

        return
        column = 17
        row = 15
        font = pygame.font.SysFont('Arial', 18)
        canvas.blit(font.render(
            "Simulation", True, pygame.Color(255, 255, 255)),
            (session.grid_2.rects_transformed[column+nrows*row][1][0][0] + 5,
             session.grid_2.rects_transformed[column+nrows*row][1][0][1] + 10)
        )

        # draw mode buffer:
        column = 20
        if session.pending_mode is not None:
            sim_string = str(round(session.pending_mode.activation_buffer_time - (
                datetime.datetime.now() - self.mode_token_selection_time).total_seconds(), 2))
            canvas.blit(font.render(sim_string, True, pygame.Color(255, 255, 255)), (
                session.grid_2.rects_transformed[column+nrows*row][1][0][0], session.grid_2.rects_transformed[column+nrows*row][1][0][1] + 40))