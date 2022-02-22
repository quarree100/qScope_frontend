''' Interface Elements needed for User Interaction '''

import pygame

import q100viz.keystone as keystone
import q100viz.session as session
from config import config

############################ SLIDER ###################################
class Slider:
    def __init__(self, canvas_size, grid, coords):
        self.coords = coords
        self.color = pygame.Color(20, 200, 150)

        self.handle = session.slider_handles[0]
        self.previous_handle = None

        # create rectangle around centerpoint:
        self.surface = keystone.Surface(canvas_size, pygame.SRCALPHA)
        self.surface.src_points = [
            [0, 0], [0, 100], [100, 100], [100, 0]]

        self.surface.dst_points = grid.surface.dst_points  # relative coordinate system

        self.surface.calculate(session.viewport.transform_mat)  # get matrix to transform by

        self.coords_transformed = self.surface.transform([
            [self.coords[0], self.coords[3]], [self.coords[0], self.coords[1]],
            [self.coords[2], self.coords[1]], [self.coords[2], self.coords[3]]])

    def render(self, canvas=None):
        # coloring slider area:
        pygame.draw.polygon(self.surface, self.color, self.coords_transformed)
        font = pygame.font.SysFont('Arial', 12)

        # show corner points:
        if session.verbose:
            self.surface.blit(font.render(str("0"), True, (255,255,255)), [self.coords_transformed[0][0] - 50, self.coords_transformed[0][1] + 50])
            self.surface.blit(font.render(str("1"), True, (255,255,255)), self.coords_transformed[1])
            self.surface.blit(font.render(str("2"), True, (255,255,255)), self.coords_transformed[2])
            self.surface.blit(font.render(str("3"), True, (255,255,255)), self.coords_transformed[3])

        canvas.blit(self.surface, (0,0))

    def transform(self):
        self.coords_transformed = self.surface.transform([
            [self.coords[0], self.coords[3]], [self.coords[0], self.coords[1]],
            [self.coords[2], self.coords[1]], [self.coords[2], self.coords[3]]])

    def update(self):
        if self.handle == 'year':
            # ranges from 2020 to 2050
            session.environment['year'] = 2020 + \
                int(grid.sliders['slider0'] * 30)
        elif self.handle == 'foerderung':
            session.environment['foerderung'] = int(
                grid.sliders['slider0'] * 10000)  # ranges from 0 to 10,000€
        elif self.handle == 'CO2-Preis':
            session.environment['CO2-Preis'] = 55 + \
                grid.sliders['slider0'] * \
                195  # ranges from 55 to 240€/t
        elif self.handle == 'CO2-emissions':
            session.buildings.loc[(
                session.buildings.selected == True), 'CO2'] = grid.sliders['slider0']  # sets CO2-value of selected buildings to slider value (absolute)
            session.print_verbose((session.buildings[session.buildings['selected'] == True]))
        elif self.handle == 'versorgung':
            if grid.sliders['slider0'] >= 0 and grid.sliders['slider0'] < 0.33:
                session.buildings.loc[(session.buildings.selected == True), 'versorgung'] = 'konventionell'
            elif grid.sliders['slider0'] >= 0.33 and grid.sliders['slider0'] < 0.66:
                session.buildings.loc[(session.buildings.selected == True), 'versorgung'] = 'medium'
            if grid.sliders['slider0'] >= 0.66 and grid.sliders['slider0'] < 1:
                session.buildings.loc[(session.buildings.selected == True), 'versorgung'] = 'gruen'
        elif self.handle == 'investment':
            # ranges from 0 to 10,000€
            session.environment['investment'] = grid.sliders['slider0'] * 10000
        elif self.handle == 'anschluss':
            session.buildings.loc[(
                session.buildings.selected == True), 'anschluss'] = grid.sliders['slider0'] > 0.5  # sets CO2-value of selected buildings to slider value (absolute)
            session.print_verbose((session.buildings[session.buildings['selected'] == True]))

############################### MODE SELECTOR #########################
class ModeSelector:
    def __init__(self, surface, rect_points):
        self.color = pygame.Color(200, 150, 20)
        self.surface = surface
        self.rect_points = rect_points

        # self.coords_transformed = self.surface.transform(rect_points)

    def render(self, canvas=None):
        # pygame.draw.polygon(self.surface, self.color, self.coords_transformed)
        pygame.draw.polygon(self.surface, self.color, self.surface.transform(self.rect_points))

        pygame.draw.rect(self.surface, self.color, pygame.Rect(50, 50, 50,50))

class MousePosition:
    def __init__(self, canvas_size):
        self.surface = keystone.Surface(canvas_size, pygame.SRCALPHA)


    def draw(self, surface, x, y):
        pygame.draw.circle(surface, pygame.color.Color(50, 160, 123), (x, y), 20)