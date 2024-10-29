import pygame
from q100viz.graphics.graphictools import Icon
from q100viz.settings.config import config
from q100viz.interaction.Slider import Slider
import q100viz.session as session

class PopupMenu:
    def __init__(self, surface, origin=(0, 0), rect_dim=(300, 250), displace=(0, 0), idx=-1, draw_border=False):

        self.icons = {
            'start_simulation': Icon("images/start_simulation.png"),
            'start_buildings_interaction': Icon("images/start_buildings_interaction.png"),
            'start_individual_data_view': Icon("images/start_individual_data_view.png"),
            'start_total_data_view': Icon("images/start_total_data_view.png"),
            'refurbished': Icon("images/refurbished.png"),
            'connection_to_heat_grid': Icon("images/connection_to_heat_grid.png"),
            'save_energy': Icon("images/save_energy.png"),
        }

        self.surface = surface

        self.origin = origin
        self.bounding_box = pygame.Rect(
            origin[0], origin[1], rect_dim[0], rect_dim[1])
        self.displace = displace
        self.dragging = False  # the menu can be moved by click&hold on address_box

        self.alpha = 0
        self.colors = {
            "user": pygame.Color(session.user_colors[session.buildings.df.loc[idx, "group"]]),
            "secondary": pygame.Color(60, 60, 60)
        }
        self.building_address = session.buildings.df.loc[idx, "address"]
        self.idx = idx
        self.slider = Slider(idx)
        self.draw_border = draw_border
        self.popup_type = None

        # center rectangle:
        self.bounding_box = self.bounding_box.move(
            displace[0] - self.bounding_box.width / 2,
            displace[1] - self.bounding_box.height / 2)

        # boxes:
        self.address_box = pygame.Rect(
            self.bounding_box.left, self.bounding_box.top, self.bounding_box.width, 30)

        self.icons_box = pygame.Rect(
            self.bounding_box.left,
            self.address_box.bottom,
            self.bounding_box.width, 
            100)
        
        self.slider.bounding_box = pygame.Rect(
            self.bounding_box.left,
            self.icons_box.bottom,
            self.bounding_box.width, 
            75)
        
        self.info_box = pygame.Rect(
            self.bounding_box.left,
            self.slider.bounding_box.bottom,
            self.bounding_box.width, 
            30)
        
        self.boxes = [self.bounding_box, self.address_box, self.icons_box, self.slider.bounding_box, self.info_box]
        
    def draw(self):
        if self.alpha < 200:
            self.alpha = min(self.alpha + 75, 200)

        # draw indication line:
        pygame.draw.line(
            self.surface,
            pygame.Color(
                self.colors["user"].r,
                self.colors["user"].g,
                self.colors["user"].b,
                self.alpha),
            self.origin, self.bounding_box.center, 4
        )

        # border:
        if self.draw_border:
            pygame.draw.rect(
                surface=self.surface,
                color=pygame.Color(
                    self.colors["user"].r,
                    self.colors["user"].g,
                    self.colors["user"].b,
                    self.alpha),
                rect=self.bounding_box.scale_by(1.2)
            )

        # ------------draw bounding box: ------------
        pygame.draw.rect(
            surface=self.surface,
            color=pygame.Color(255, 255, 255, 50),
            rect=self.bounding_box
            )

        # ------------draw address box: ------------
        pygame.draw.rect(
            surface=self.surface,
            color=pygame.Color(
                self.colors["user"].r,
                    self.colors["user"].g,
                    self.colors["user"].b,
                    self.alpha
                ),
            rect=self.address_box
        )

        # address name:
        font = pygame.font.SysFont('Arial', 20)
        text = font.render(self.building_address, True,
                           pygame.Color(255, 255, 255))
        self.surface.blit(text, text.get_rect(
            center=(self.address_box.centerx, self.address_box.centery)))

        num_of_images = 3
        spacing = self.bounding_box.width / num_of_images

        pygame.draw.rect(
            surface=self.surface,
            color=pygame.Color(55, 120, 255, 80),
            rect=self.icons_box
        )
        
        # --------------- icons: ---------------
        for i, key in enumerate(session.VALID_DECISION_HANDLES):

            self.icons[key].rect = pygame.Rect(
                self.icons_box.left + 0.25 * spacing + i * spacing,
                self.icons_box.top + (self.icons_box.height - self.icons[key].image.height) / 2,
                self.icons[key].image.width,
                self.icons[key].image.height
            )

            # border if image selected
            if self.icons[key].selected:
                pygame.draw.rect(
                    surface=self.surface,
                    color=pygame.Color(255, 120, 55),
                    rect=self.icons[key].rect.scale_by(1.3)
                )

            # image:
            self.surface.blit(
                self.icons[key].image,
                self.icons[key].rect.topleft
            )

        # ------------ slider if any handle selected ---------
        if any(icon.selected for icon in self.icons.values()):
            pygame.draw.rect(
                self.surface,
                pygame.Color(200, 200, 200),
                self.slider.bounding_box,
                border_radius=int(self.slider.bounding_box.height/2) if self.popup_type == "switch" else 0
            )
            
            if self.popup_type == "slider":
                # draw vertical line
                pygame.draw.line(
                    self.surface,
                    pygame.Color(10, 10, 240),
                    (self.slider.bounding_box.left + self.slider.value * self.slider.bounding_box.width, self.slider.bounding_box.top),
                    (self.slider.bounding_box.left + self.slider.value * self.slider.bounding_box.width, self.slider.bounding_box.bottom), 
                    4
                )
            elif self.popup_type == "switch":
                pygame.draw.circle(
                    surface=self.surface,
                    color=pygame.Color(250, 250, 250),
                    center=(self.slider.bounding_box.left + self.slider.bounding_box.height / 2 if self.slider.value < 0.5 else self.slider.bounding_box.right - self.slider.bounding_box.height / 2, self.slider.bounding_box.centery),
                    radius=self.slider.bounding_box.height / 2
                )
            
            # info text:
            font = pygame.font.SysFont('Arial', 20)
            text = font.render(
                self.slider.human_readable_handle[self.slider.handle] + ": " + str(self.slider.human_readable_value[self.slider.handle]), 
                True,
                pygame.Color(255, 255, 255)
            )
            self.surface.blit(text, (self.info_box.left + 0.05 * self.info_box.width, self.info_box.centery))


    def handle_mouse_button(self, mouse_pos):           
        # drag
        if self.address_box.collidepoint(mouse_pos):
            self.dragging = True
            self.drag_offset = [(
                mouse_pos[0] - box.left,
                mouse_pos[1] - box.top) for box in self.boxes]
            return
        
        # open slider:
        for key in self.icons.keys():
            icon = self.icons[key]
            if icon.rect.collidepoint(mouse_pos):
                if any(ic.selected for ic in self.icons.values()):
                    for ic in self.icons.values():
                        ic.selected = False
                icon.selected = not icon.selected
                self.slider.handle = key
                if key in ["connection_to_heat_grid", "refurbished"]:
                    self.popup_type = "slider"
                    # reset slider_box layout:
                    self.slider.bounding_box.update(
                        self.bounding_box.left,
                        self.icons_box.bottom,
                        self.bounding_box.width, 
                        75)                    
                elif key in ["save_energy"]:
                    self.popup_type = "switch"
                    # change slider_box layout:
                    self.slider.bounding_box.width = self.bounding_box.height / 2
                    self.slider.bounding_box.centerx = self.bounding_box.centerx
                    
                self.slider.process_value(True)
            
        # switch clicked:
        if self.slider.bounding_box.collidepoint(mouse_pos) and self.popup_type == "switch":
            session.buildings.df.at[self.idx, key] = not session.buildings.df.loc[self.idx, key]
            self.slider.value = 1 if self.slider.value < 0.5 else 0
            self.slider.process_value()
            print(self.slider.value)

                
    def handle_mouse_motion(self, mouse_pos):       
        if self.popup_type == "slider" and any(ic.selected for ic in self.icons.values()):        
            if self.slider.bounding_box.collidepoint(mouse_pos):
                self.slider.update_from_interaction(mouse_pos)
                self.slider.process_value()
