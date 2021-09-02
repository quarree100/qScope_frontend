import json
import pygame

import q100viz.keystone as keystone


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
        rects_transformed = [
            (cell, self.surface.transform([[x, y], [x, y + 1], [x + 1, y + 1], [x + 1, y]]))
            for y, row in enumerate(self.grid) for x, cell in enumerate(row)]

        font = pygame.font.SysFont('Arial', 20)

        # draw grid data
        for cell, rect_points in rects_transformed:
            self.surface.blit(
                font.render(str(cell.id), True, (255, 255, 255)),
                rect_points[0]
            )
            self.surface.blit(
                font.render(str(cell.rot), True, (255, 255, 0)),
                [rect_points[0][0] + 20, rect_points[0][1]]
            )
            self.surface.blit(
                font.render(str(cell.rel_rot), True, (255, 127, 0)),
                [rect_points[0][0] + 20, rect_points[0][1] + 20]
            )

        # draw rectangle outlines
        for cell, rect_points in rects_transformed:
            stroke = 4 if cell.selected else 1
            pygame.draw.polygon(self.surface, pygame.Color(255, 255, 255), rect_points, stroke)

    def mouse_pressed(self, button):
        pos = pygame.mouse.get_pos()

        # get grid coordinate
        coord = self.surface.inverse_transform([pos])[0]

        if coord[0] < 0 or coord[1] < 0:
            return

        # update cell at cursor position
        try:
            cell = self.grid[int(coord[1])][int(coord[0])]
            if button == 1:  # left click
                cell.selected = not cell.selected
            elif button == 3:  # right click
                cell.prev_rot = cell.rot
                cell.rot  = (cell.rot + 1) % 4
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
                    cell.id, cell.rot = array[y * self.x_size + x]

                    # any non-white object selects cells
                    cell.selected = cell.id != 0

                    # calculate relative rotation
                    # an inactive cell has a rotation value of -1
                    if cell.rot == -1:
                        cell.rel_rot = 0
                    elif cell.prev_rot != cell.rot:
                        cell.rel_rot = cell.rot - cell.prev_rot if cell.prev_rot > -1 else 0
                    cell.prev_rot = cell.rot

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
        self.prev_rot = -1
        self.rel_rot = 0
        self.selected = False
