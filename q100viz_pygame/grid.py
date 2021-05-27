import pygame

import keystone

class Grid:
    def __init__(self, canvas_size, xmin, ymin, xmax, ymax, x_size, y_size):
        self.x_size = x_size
        self.y_size = y_size

        # create a surface with per-pixel alpha
        self.surface = keystone.Surface(canvas_size, pygame.SRCALPHA)

        # calculate the projection matrix (grid coordinates -> viewport coordinates)
        self.surface.src_points = [[0, 0], [0, y_size], [x_size, 0], [x_size, y_size]]
        self.surface.dst_points = [[xmin, ymin], [xmin, ymax], [xmax, ymin], [xmax, ymax]]
        self.surface.calculate()

        # initialize two-dimensional array of grid cells
        self.grid = [[GridCell() for x in range(x_size)] for y in range(y_size)]

    def draw(self, surface):
        colors = [
            (180, 180, 180),
            (255, 255, 255),
            (50, 50, 125),
            (255, 255, 0),
            (0, 255, 255),
            (0, 100, 255),
            (100, 255, 100)
        ]

        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                stroke = 4 if cell.selected else 1
                fill = pygame.Color(*colors[cell.id]) if cell.id > -1 else pygame.Color(255, 255, 255)

                p0, p1 = (x, y), (x + 1, y + 1)
                p0_t, p1_t = self.surface.transform([p0, p1])
                pygame.draw.rect(self.surface, fill, (*p0_t, p1_t[0] - p0_t[0], p1_t[1] - p0_t[1]), stroke)


class GridCell:
    def __init__(self, id=-1, rot=-1):
        self.id = id
        self.rot = rot
        self.selected = False

