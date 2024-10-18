import pygame
from q100viz.graphics.graphictools import Icon
from q100viz.settings.config import config
import q100viz.session as session

class PopupMenu:
    def __init__(self, surface, origin=(0, 0), rect_dim=(300, 250), displace=(0, 0), building_address="", draw_border=False):

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

        self.alpha = 0
        self.colors = {
            "user": pygame.Color(120, 130, 240),  # TODO: use user colors
            "secondary": pygame.Color(60, 60, 60)
        }
        self.building_address = building_address
        self.slider_value = 0
        self.draw_border = draw_border

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
        
        self.slider_box = pygame.Rect(
            self.bounding_box.left,
            self.icons_box.bottom,
            self.bounding_box.width, 
            75)
        
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

        # ------------bounding box: ------------
        pygame.draw.rect(
            surface=self.surface,
            color=pygame.Color(255, 255, 255),
            rect=self.bounding_box
        )

        # ------------address box: ------------
        pygame.draw.rect(
            surface=self.surface,
            color=pygame.Color(255, 0, 0),
            rect=self.address_box
        )

        # address name:
        font = pygame.font.SysFont('Arial', 20)
        text = font.render(self.building_address, True,
                           pygame.Color(255, 255, 255))
        self.surface.blit(text, text.get_rect(
            center=(self.address_box.left + 0.5 * self.address_box.width, self.address_box.centery)))

        num_of_images = 3
        spacing = self.bounding_box.width / num_of_images

        pygame.draw.rect(
            surface=self.surface,
            color=pygame.Color(55, 120, 255, 80),
            rect=self.icons_box
        )
        
        # --------------- icons: ---------------
        for i, key in enumerate(["connection_to_heat_grid", "refurbished", "save_energy"]):

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

        # slider if any image selected
        if any(icon.selected for icon in self.icons.values()):
            pygame.draw.rect(
                self.surface,
                pygame.Color(111, 200, 67),
                self.slider_box
            )
            
            pygame.draw.line(
                self.surface,
                pygame.Color(10, 10, 240),
                (self.bounding_box.left + self.slider_value * self.bounding_box.width, self.slider_box.top),
                (self.bounding_box.left + self.slider_value * self.bounding_box.width, self.slider_box.bottom), 
                4
            )

    def handle_mouse_button(self, mouse_pos):           
        # iterate images
        for key in self.icons.keys():
            icon = self.icons[key]
            if icon.rect.collidepoint(mouse_pos):
                if any(ic.selected for ic in self.icons.values()):
                    for ic in self.icons.values():
                        ic.selected = False
                icon.selected = not icon.selected

    def handle_mouse_motion(self, mouse_pos):
        if any(ic.selected for ic in self.icons.values()):        
            if self.slider_box.collidepoint(mouse_pos):
                self.slider_value = (mouse_pos[0] - self.slider_box.left) / self.bounding_box.width
                print(self.slider_value)