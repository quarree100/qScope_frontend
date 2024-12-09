import numpy as np
import pygame
from q100viz.graphics.graphictools import Icon
from q100viz.interaction.Slider import Slider
import q100viz.session as session
import q100viz.graphics.graphictools as graphictools

class TouchMenu:
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
        self.visible = True

        self.origin = origin  # usually center of building
        self.bounding_box = pygame.Rect(
            origin[0], origin[1], rect_dim[0], rect_dim[1])
        self.displace = displace
        self.dragging = False  # the menu can be moved by click&hold on address_box

        self.alpha = 0
        self.colors = {
            "user": pygame.Color(session.user_colors[session.buildings.df.loc[idx, "group"]]),
            "interactive": pygame.Color(222, 222, 222),
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

        session.buildings.df.at[idx, 'popup'] = self
        session.popup_menus[idx] = self
        
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
                color=pygame.Color(
                    self.colors["user"].r,
                    self.colors["user"].g,
                    self.colors["user"].b,
                    self.alpha / 2),
            rect=self.bounding_box
            )

        # ------------draw address box: ------------
        pygame.draw.rect(
            surface=self.surface,
                color=pygame.Color(
                    self.colors["user"].r,
                    self.colors["user"].g,
                    self.colors["user"].b,
                    self.alpha),
            rect=self.address_box
        )

        # address name:
        font = pygame.font.SysFont('Arial', 20)
        text = font.render(self.building_address, True,
                           pygame.Color(255, 255, 255))
        self.surface.blit(text, text.get_rect(
            center=(self.address_box.centerx, self.address_box.centery)))
            
        # --------------- icons: ---------------
        num_of_images = 3
        spacing = self.bounding_box.width / num_of_images

        pygame.draw.rect(
            surface=self.surface,
                color=pygame.Color(
                    self.colors["user"].r,
                    self.colors["user"].g,
                    self.colors["user"].b,
                    self.alpha / 2),
                rect=self.icons_box
        )
        
        for i, key in enumerate(session.VALID_DECISION_HANDLES):

            # reset icons rectangle:
            self.icons[key].rect = pygame.Rect(
                self.icons_box.left + 0.25 * spacing + i * spacing,
                self.icons_box.top + (self.icons_box.height - self.icons[key].image.height) / 2,
                self.icons[key].image.width,
                self.icons[key].image.height
            )

            # highlight if image selected
            pygame.draw.rect(
                surface=self.surface,
                color=self.colors["user"] if self.icons[key].selected else self.colors["interactive"],
                rect=self.icons[key].rect.scale_by(1.3),
                border_radius=self.icons[key].rect.width
            )

            # image:
            self.surface.blit(
                self.icons[key].image,
                self.icons[key].rect.topleft
            )
            
            text = pygame.font.SysFont('Arial', 16).render(
                session.buildings.human_readable_value(key, self.idx), True, (255, 255, 255)
            )
            self.surface.blit(text, text.get_rect(centerx=self.icons[key].rect.scale_by(1.3).centerx, top=self.icons[key].rect.scale_by(1.3).bottom))

        # ------------ slider if any handle selected ---------
        if any(icon.selected for icon in self.icons.values()):
            # slider box
            color = self.colors["user"] if session.buildings.df.loc[self.idx, 'save_energy'] or self.popup_type == "slider" else pygame.Color(200, 200, 200)
            pygame.draw.rect(
                surface=self.surface,
                color=color,
                rect=self.slider.bounding_box,
                border_radius=int(self.slider.bounding_box.height/2)
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
            return True
        
        # decision buttons:
        for key in self.icons.keys():
            icon = self.icons[key]
            if icon.rect.collidepoint(mouse_pos):
                if any(ic.selected for ic in self.icons.values()):
                    for ic in self.icons.values():
                        ic.selected = False
                icon.selected = not icon.selected
                self.slider.handle = key
                # open slider / change layout:
                if key in ["connection_to_heat_grid", "refurbished"]:
                    self.popup_type = "slider"
                    self.slider.bounding_box.update(
                        self.bounding_box.left,
                        self.icons_box.bottom,
                        self.bounding_box.width, 
                        75)                    
                elif key in ["save_energy"]:
                    self.popup_type = "switch"
                    self.slider.bounding_box.width = self.bounding_box.height / 2
                    self.slider.bounding_box.centerx = self.bounding_box.centerx
                    
                self.slider.process_value(True)
                return True
            
        # switch clicked:
        if self.slider.bounding_box.collidepoint(mouse_pos) and self.popup_type == "switch":
            session.buildings.df.at[self.idx, key] = not session.buildings.df.loc[self.idx, key]
            self.slider.value = 1 if self.slider.value < 0.5 else 0
            self.slider.process_value()
            return True
        
        return False
                
    def handle_mouse_motion(self, mouse_pos):       
        if self.popup_type == "slider" and any(ic.selected for ic in self.icons.values()):        
            if self.slider.bounding_box.collidepoint(mouse_pos):
                self.slider.update_from_interaction(mouse_pos)
                self.slider.process_value()

    def destroy(self):
        if not session.buildings.df.at[self.idx, 'popup']: return
        session.buildings.df.at[self.idx, 'popup'] = None
        del session.popup_menus[self.idx]


class TangibleMenu(TouchMenu):
    
    def __init__(self, surface, origin, rect_dim=(300, 250), displace=(0, 0), idx=-1, draw_border=False, start_rotation=0):
        super().__init__(surface, origin, rect_dim, displace, idx, draw_border)
        self.radius = 0
        self.start_rotation = start_rotation
        self.current_rotation = 0
        
        self.address_box = pygame.Rect(
            origin, (self.bounding_box.width, 30))        
        
    def process_rotation(self, angle):
        if not (any([ic.selected for ic in self.icons.values()])):
            self.current_rotation = -((self.start_rotation - angle) % 360)
        else:
            self.slider.value = 1 - (((self.start_rotation - angle) % 360) / 360)
            self.slider.process_value()

    def draw(self):
        if self.alpha < 200:
            self.alpha = min(self.alpha + 75, 200)
        radius_target = np.linalg.norm(self.displace) * 0.8
        if self.radius < radius_target:
            self.radius = min(self.radius + 50, radius_target)

        # draw indication line:
        rot = self.current_rotation + 15
        for key in session.VALID_DECISION_HANDLES:
            x = self.origin[0] + np.cos(np.deg2rad(rot)) * self.radius
            y = self.origin[1] + np.sin(np.deg2rad(rot)) * self.radius
            pygame.draw.line(
                self.surface,
                pygame.Color(
                    self.colors["user"].r,
                    self.colors["user"].g,
                    self.colors["user"].b,
                    self.alpha),
                self.origin, (x, y), 4
            )
            rot += 75

            # --------------------- icons: ----------------------------
            self.icons[key].rect = pygame.Rect(
                x, y,
                self.icons[key].image.width,
                self.icons[key].image.height
            )
            self.icons[key].rect.center = (x, y)
            
            # highlight if image selected 
            color_key = "user" if self.icons[key].selected else "interactive"
            pygame.draw.rect(
                surface=self.surface,
                color=pygame.Color(
                    self.colors[color_key].r,
                    self.colors[color_key].g,
                    self.colors[color_key].b,
                    session.global_alpha),
                rect=self.icons[key].rect.scale_by(1.7),
                border_radius=self.icons[key].rect.width
            )

            self.surface.blit(
                self.icons[key].image,
                self.icons[key].rect.topleft
            )
            
            # ---------------------- info text: -----------------------
            font = pygame.font.SysFont('Arial', 20)
            text = font.render(
                str(self.slider.human_readable_value[key]), 
                True,
                pygame.Color(255, 255, 255)
            )            
            
            self.surface.blit(text, text.get_rect(center=(x, y + 20)))            
            
        # ---------------- address and energy bar: ----------------
        font = pygame.font.SysFont('Arial', 20)
        text = font.render(f"{self.building_address}\nEnergieklasse: {session.buildings.consumption_to_energy_class(session.buildings.df.loc[self.idx, 'spec_heat_consumption'])}", True,
                           pygame.Color(255, 255, 255))
        if self.building_address:
            
            self.address_box.width = text.get_rect().width + 40               
            self.address_box.height = text.get_rect().height + 20           

            x = self.origin[0] + np.cos(np.deg2rad(self.current_rotation + 90)) * 60
            y = self.origin[1] + np.sin(np.deg2rad(self.current_rotation + 90)) * 60

            self.address_box.center = (x, y)
            
            # draw address box:
            pygame.draw.rect(
                surface=self.surface,
                    color=pygame.Color(
                        self.colors["user"].r,
                        self.colors["user"].g,
                        self.colors["user"].b,
                        self.alpha),
                rect=self.address_box
            )
            
            # address name:
            self.surface.blit(text, text.get_rect(
                center=self.address_box.center))
        
        # ---------------------- info text: -----------------------
        font = pygame.font.SysFont('Arial', 20)
        text = font.render(
            str(self.slider.human_readable_value[key]), 
            True,
            pygame.Color(255, 255, 255)
        )            
        
        self.surface.blit(text, text.get_rect(center=(x, y + 20)))
        
        # draw pie:
        if (any([ic.selected for ic in self.icons.values()])):
            graphictools.draw_pie(self.surface, pygame.Color(255, 0, 0.5), self.origin, self.radius * 0.5, 0, self.slider.value * 360, 0.1)
            
