import json
import pygame

import q100viz.keystone as keystone
import q100viz.session as session


class Grid:
    def __init__(self, canvas_size, x_size, y_size, dst_points, viewport, slider_ids=[]):
        self.x_size = x_size
        self.y_size = y_size

        # create a surface with per-pixel alpha
        self.surface = keystone.Surface(canvas_size, pygame.SRCALPHA)

        # calculate the projection matrix (grid coordinates -> canvas coordinates)
        self.surface.src_points = [[0, 0], [0, y_size], [x_size, y_size], [x_size, 0]]
        self.surface.dst_points = dst_points
        self.surface.calculate(viewport.transform_mat)

        # initialize two-dimensional array of grid cells
        self.grid = [[GridCell(x, y) for x in range(x_size)] for y in range(y_size)]

        # create a list of transformed rectangles
        self.rects_transformed = [
            (cell, self.surface.transform([[x, y], [x, y + 1], [x + 1, y + 1], [x + 1, y]]))
            for y, row in enumerate(self.grid) for x, cell in enumerate(row)]

        # set up sliders
        self.sliders = {slider_id: None for slider_id in slider_ids}

        # list of transformed slider controls rectangles
        # self.slider_controls_transformed = [
        #     (cell, self.surface.transform([[x, y], [x, y + 1], [x + 1, y + 1], [x + 1, y]]))
        #     for y, row in enumerate(self.slider_controls) for x, cell in enumerate(row)]

    def draw(self, surface, show_grid):

        font = pygame.font.SysFont('Arial', 20)

        # draw grid data
        if show_grid:
            for cell, rect_points in self.rects_transformed:
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
        for cell, rect_points in self.rects_transformed:
            # do not apply to last row; it will be treated seperatedly as slider controls:
            if cell.y is not len(self.grid) - 1 and show_grid:
                stroke = 4 if cell.selected else 1
                pygame.draw.polygon(self.surface, pygame.Color(255, 255, 255), rect_points, stroke)

            # print function on sliderControl cells:
            if cell.y == len(self.grid) - 1:
                if cell.x % 3 == 0:
                    font = pygame.font.SysFont('Arial', 14)
                    self.surface.blit(
                        font.render(session.slider_handles[
                            int(cell.x/(session.grid_settings['ncols']/(len(session.slider_handles) - 1)))],
                            True, (255, 255, 255)),
                            [rect_points[0][0], rect_points[0][1]]
                    )

                # draw slider controls:
                cell_color = pygame.Color(20, 200, 150)
                stroke = 4 if cell.selected else 1
                # colors via slider parameter fields:
                if cell.x >= 0 and cell.x < 3:
                    cell_color = pygame.Color(73, 156, 156)
                elif cell.x >= 3 and cell.x < 6:
                    cell_color = pygame.Color(126, 185, 207)
                elif cell.x >= 6 and cell.x < 9:
                    cell_color = pygame.Color(247, 79, 115)
                elif cell.x >= 9 and cell.x < 12:
                    cell_color = pygame.Color(193, 135, 77)
                elif cell.x >= 12 and cell.x < 15:
                    cell_color = pygame.Color(187, 210, 4)
                elif cell.x >= 15 and cell.x < 18:
                    cell_color = pygame.Color(249, 109, 175)
                elif cell.x >= 18 and cell.x < 21:
                    cell_color = pygame.Color(9, 221, 250)
                elif cell.x >= 21 and cell.x < 24:
                    cell_color = pygame.Color(150, 47, 28)

                if cell.selected:
                    session.slider.color = cell_color

                pygame.draw.polygon(surface, cell_color, rect_points, stroke)


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
            msg = json.loads(message)
        except json.decoder.JSONDecodeError:
            print("Invalid JSON")
            return

        try:
            # update grid cells
            for y, row in enumerate(self.grid):
                for x, cell in enumerate(row):
                    cell.id, cell.rot = msg['grid'][y * self.x_size + x]

                    cell.selected = cell.id != 0  # any non-white object selects cells

                    # calculate relative rotation
                    # an inactive cell has a rotation value of -1
                    if cell.rot == -1:
                        cell.rel_rot = 0
                    elif cell.prev_rot != cell.rot:
                        cell.rel_rot = cell.rot - cell.prev_rot if cell.prev_rot > -1 else 0
                    cell.prev_rot = cell.rot

            # update slider values
            for slider_id in self.sliders.keys():
                self.sliders[slider_id] = msg['sliders'][slider_id]

        except TypeError:
            pass
        except IndexError:
            print("Warning: incoming grid data is incomplete")

    def print(self):
        try:
            for row in self.grid:
                for cell in row:
                    print(f"{cell.id}/{cell.rot}", end="\t")
                print()
            print()
        except TypeError:
            pass

    def transform(self):
        self.rects_transformed = [
            (cell, self.surface.transform([[x, y], [x, y + 1], [x + 1, y + 1], [x + 1, y]]))
            for y, row in enumerate(self.grid) for x, cell in enumerate(row)]

class GridCell:
    def __init__(self, x, y, id=-1, rot=-1):
        self.x = x
        self.y = y
        self.id = id
        self.rot = rot
        self.prev_rot = -1
        self.rel_rot = 0
        self.selected = False
