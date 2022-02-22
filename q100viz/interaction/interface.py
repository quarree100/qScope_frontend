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

class MousePosition:
    def __init__(self, canvas_size):
        self.surface = keystone.Surface(canvas_size, pygame.SRCALPHA)


    def draw(self, surface, x, y):
        pygame.draw.circle(surface, pygame.color.Color(50, 160, 123), (x, y), 20)