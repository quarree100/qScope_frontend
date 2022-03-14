''' Interface Elements needed for User Interaction '''

import pygame
import json

import q100viz.keystone as keystone
import q100viz.session as session

from config import config

############################ SLIDER ###################################
class Slider:
    def __init__(self, canvas_size, grid, coords):
        self.value = 0
        self.previous_value = 0
        self.show_text = True  # display slider control text on grid
        self.show_controls = True

        self.color = pygame.Color(20, 200, 150)

        self.handle = None
        self.previous_handle = None

        self.grid = grid

        # create rectangle around centerpoint:
        self.surface = keystone.Surface(canvas_size, pygame.SRCALPHA)
        self.surface.src_points = [
            [0, 0], [0, 100], [100, 100], [100, 0]]

        self.surface.dst_points = grid.surface.dst_points  # relative coordinate system

        self.surface.calculate(session.viewport.transform_mat)  # get matrix to transform by

        self.coords_transformed = self.surface.transform(coords)

    def render(self, canvas=None):
        canvas.blit(self.surface, (0,0))

        # print function text on sliderControl cells:
        for cell, rect_points in self.grid.rects_transformed:
            if cell.y == len(self.grid.grid) - 1:
                if cell.x < session.grid_settings['ncols'] / 2:
                    if cell.x % int((session.grid_settings['ncols'] / 2 / len(session.slider_handles))) == 0 and self.show_text:
                        index = int(cell.x / ((session.grid_settings['ncols'] / 2) / len(session.slider_handles)))
                        font = pygame.font.SysFont('Arial', 8)
                        self.grid.surface.blit(
                            font.render(session.slider_handles[index],
                                True, (255, 255, 255)),
                                [rect_points[0][0] + 10, rect_points[0][1]+ 35]
                        )

                    # slider control colors:
                    if self.show_controls:
                        cell_color = pygame.Color(20, 200, 150)
                        stroke = 4 if cell.selected else 1
                        # colors via slider parameter fields:
                        colors = [
                            (73, 156, 156),
                            (126, 185, 207),
                            (247, 79, 115),
                            (193, 135, 77),
                            (187, 210, 4),
                            (249, 109, 175),
                            (9, 221, 250),
                            (150, 47, 28)]

                        index = int(cell.x / ((session.grid_settings['ncols'] / 2) / len(session.slider_handles)))
                        cell_color = pygame.Color(colors[index])

                        if cell.selected:
                            self.color = cell_color

                        if session.show_polygons: pygame.draw.polygon(self.grid.surface, cell_color, rect_points, stroke)

    def transform(self):
        self.coords_transformed = self.surface.transform([
            [self.coords[0], self.coords[3]], [self.coords[0], self.coords[1]],
            [self.coords[2], self.coords[1]], [self.coords[2], self.coords[3]]])

    def update(self):
        ''' TODO: set up a struct (maybe csv) to import standard values >> this section should be automatized!
        e.g.
        if self.handle == 'name':
            session.environment['name'] = val_from_struct * slider_val
        '''

        # globals:
        if self.handle == 'year':
            session.environment['year'] = 2020 + \
                int(self.value * 30) # ranges from 2020 to 2050
        elif self.handle == 'foerderung':
            session.environment['foerderung'] = int(
                self.value * 10000)  # ranges from 0 to 10,000€
        elif self.handle == 'CO2-Preis':
            session.environment['CO2-Preis'] = 55 + \
                self.value * 195  # ranges from 55 to 240€/t
        elif self.handle == 'connection_speed':
            session.environment['connection_speed'] = self.value

        # household-specific:
        elif self.handle == 'CO2-emissions':
            session.buildings.loc[(
                session.buildings.selected == True), 'CO2'] = self.value  # sets CO2-value of selected buildings to slider value (absolute)
            session.print_verbose((session.buildings[session.buildings['selected'] == True]))
        elif self.handle == 'versorgung':
            if self.value >= 0 and self.value < 0.33:
                session.buildings.loc[(session.buildings.selected == True), 'versorgung'] = 'konventionell'
            elif self.value >= 0.33 and self.value < 0.66:
                session.buildings.loc[(session.buildings.selected == True), 'versorgung'] = 'medium'
            if self.value >= 0.66 and self.value < 1:
                session.buildings.loc[(session.buildings.selected == True), 'versorgung'] = 'gruen'
        elif self.handle == 'investment':
            # ranges from 0 to 10,000€
            session.environment['investment'] = self.value * 10000
        elif self.handle == 'anschluss':
            session.buildings.loc[(
                session.buildings.selected == True), 'anschluss'] = self.value > 0.5  # sets CO2-value of selected buildings to slider value (absolute)
            session.print_verbose((session.buildings[session.buildings['selected'] == True]))

        # questionnaire:
        elif self.handle == 'yes_no':
            if self.value >= 0.5:
                session.environment['answer'] = 'no'
            else:
                session.environment['answer'] = 'yes'

        if self.previous_value is not self.value:
            print(self.handle)
            session.stats.send_message(json.dumps(session.environment))
            self.previous_value = self.value

############################### MODE SELECTOR #########################
class ModeSelector:
    def __init__(self, grid, x, color, name):
        self.show = True
        self.color = pygame.Color(color)
        self.grid = grid
        self.x = x
        self.name = name

    def render(self):

        if self.show:
            for cell, rect_points in self.grid.rects_transformed:
                if cell.y == len(self.grid.grid) - 1:
                    # ModeSelector
                    if cell.x == self.x:  # TODO: global positions of mode selectors (also used in intput_mode)
                        stroke = 4 if cell.selected else 1
                        pygame.draw.polygon(self.grid.surface, self.color, rect_points, stroke)
                        font = pygame.font.SysFont('Arial', 8)

                        # display mode name
                        self.grid.surface.blit(
                            font.render(self.name,
                                True, (255, 255, 255)),
                                [rect_points[0][0] + 10, rect_points[0][1]+ 35]
                        )

class MousePosition:
    def __init__(self, canvas_size):
        self.surface = keystone.Surface(canvas_size, pygame.SRCALPHA)


    def draw(self, surface, x, y):
        pygame.draw.circle(surface, pygame.color.Color(50, 160, 123), (x, y), 20)

class Rectangle:
    def __init__(self, surface):
        pass

    def draw(surface):
        pygame.draw.rect(surface, color, [[20, 70], [20, 20], [80, 20], [80, 70]])