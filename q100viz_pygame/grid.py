import json
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
            (0, 0, 0, 0),
            (255, 255, 255),
            (50, 50, 125),
            (255, 255, 0),
            (0, 255, 255),
            (0, 100, 255),
            (100, 255, 100)
        ]

        rects_transformed = [(cell, self.surface.transform([[x, y], [x, y + 1], [x + 1, y + 1], [x + 1, y]]))
            for y, row in enumerate(self.grid) for x, cell in enumerate(row)]

        # draw filled rectangles to visualize grid data
        for cell, rect_points in rects_transformed:
            if cell.id > -1:
                pygame.draw.polygon(self.surface, pygame.Color(*colors[cell.id]), rect_points, 0)

        # draw rectangle outlines
        for cell, rect_points in rects_transformed:
            stroke = 4 if cell.selected else 1
            pygame.draw.polygon(self.surface, pygame.Color(255, 255, 255), rect_points, stroke)

    def mouse_pressed(self):
        pos = pygame.mouse.get_pos()

        # get grid coordinate
        coord = self.surface.inverse_transform([pos])[0]

        if coord[0] < 0 or coord[1] < 0:
            return

        # update cell at cursor position
        try:
            cell = self.grid[int(coord[1])][int(coord[0])]
            cell.selected = not cell.selected
        except IndexError:
            pass

    def read_scanner_data(self, message):
        try:
            array = json.loads(message)
        except json.decoder.JSONDecodeError:
            print("Invalid JSON")
            return

        # update grid cells
        try:
            for y, row in enumerate(self.grid):
                for x, cell in enumerate(row):
                    cell.id, cell.rot = array[y * self.y_size + x]
                    cell.selected = False

                    # object with ID 1 selects cells
                    if cell.id == 1:
                        cell.selected = True
        except TypeError:
            pass
        except IndexError:
            print("Warning: incoming grid has unexpected size")

    def print(self):
        try:
            for row in self.grid:
                for cell in row:
                    print(f"{cell.id}/{cell.rot}", end="\t")
                print()
            print()
        except TypeError:
            pass


class GridCell:
    def __init__(self, id=-1, rot=-1):
        self.id = id
        self.rot = rot
        self.selected = False
