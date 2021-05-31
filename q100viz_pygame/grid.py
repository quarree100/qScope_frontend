import pygame

import keystone

class Grid:
    def __init__(self, canvas_size, x_size, y_size, dst_points, viewport):
        self.x_size = x_size
        self.y_size = y_size

        # create a surface with per-pixel alpha
        self.surface = keystone.Surface(canvas_size, pygame.SRCALPHA)

        # calculate the projection matrix (grid coordinates -> canvas coordinates)
        self.surface.src_points = [[0, 0], [0, y_size], [x_size, y_size], [x_size, 0]]
        self.surface.dst_points = dst_points
        self.surface.calculate(viewport.transform_mat)

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

        self.surface.fill(0)

        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                stroke = 4 if cell.selected else 1
                fill = pygame.Color(*colors[cell.id]) if cell.id > -1 else pygame.Color(255, 255, 255)

                rect_points = self.surface.transform([[x, y], [x, y + 1], [x + 1, y + 1], [x + 1, y]])
                pygame.draw.polygon(self.surface, fill, rect_points, stroke)

    def mouse_pressed(self):
        pos = pygame.mouse.get_pos()

        # get grid coordinate
        coord = self.surface.inverse_transform([pos])[0]

        # update cell at cursor position
        try:
            cell = self.grid[int(coord[1])][int(coord[0])]
            cell.selected = not cell.selected
        except IndexError:
            pass


class GridCell:
    def __init__(self, id=-1, rot=-1):
        self.id = id
        self.rot = rot
        self.selected = False

