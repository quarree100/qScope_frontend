import json
import pygame
import pandas

import q100viz.keystone as keystone
import q100viz.session as session
from q100viz.interaction.interface import Slider

class Grid:
    def __init__(self, canvas_size, x_size, y_size, dst_points, viewport, setup_data, sliders_coords, sliders_x_range):
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

        # load cell-specific information from csv:
        self.update_cell_data(pandas.read_csv(setup_data))

        # create a list of transformed rectangles
        self.rects_transformed = [
            (cell, self.surface.transform([[x, y], [x, y + 1], [x + 1, y + 1], [x + 1, y]]))
            for y, row in enumerate(self.grid) for x, cell in enumerate(row)]

        self.sliders = {
            slider_id : Slider(
                canvas_size, self, slider_id, sliders_coords[slider_id], sliders_x_range[slider_id])
            for slider_id in sliders_coords.keys()
            }

    def draw(self, show_grid):


        # draw grid data
        if show_grid:
            for cell, rect_points in self.rects_transformed:
                font = pygame.font.SysFont('Arial', 20)

                self.surface.blit(
                    font.render(str(cell.id), True, (255, 255, 255)),
                    rect_points[0]
                )
                self.surface.blit(
                    font.render(str(cell.rot), True, (255, 255, 0)),
                    [rect_points[0][0] + 20, rect_points[0][1]]
                )

                font = pygame.font.SysFont('Arial', 10)

                self.surface.blit(
                    font.render(str(cell.x) + "," + str(cell.y), True, (230, 230, 230)),
                    [rect_points[0][0], rect_points[0][1] + 20]
                )
                # self.surface.blit(
                #     font.render(str(cell.rel_rot), True, (255, 127, 0)),
                #     [rect_points[0][0] + 20, rect_points[0][1] + 20]
                # )

        # draw rectangle outlines
        for cell, rect_points in self.rects_transformed:
            # do not apply to last row; it will be treated seperatedly as slider controls:
            if cell.y is not len(self.grid) - 1 and show_grid:
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
            if button == 1:  # left click: (de)select
                cell.selected = not cell.selected
            elif button == 2:  # middle click: change id
                cell.id = (cell.id + 1) % 4
            elif button == 3:  # right click: change rotation
                cell.prev_rot = cell.rot
                cell.rot  = (cell.rot + 1) % 4
        except IndexError:
            pass  # not this grid

    def deselect(self, x_deselect, y_deselect):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell.x == x_deselect and cell.y == y_deselect:
                    cell.selected = False

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

                    cell.selected = cell.id != 5  # any non-white object selects cells

                    # calculate relative rotation
                    if cell.rot == -1:  # an inactive cell has a rotation value of -1
                        cell.rel_rot = 0
                    elif cell.prev_rot != cell.rot:
                        cell.rel_rot = cell.rot - cell.prev_rot if cell.prev_rot > -1 else 0
                    cell.prev_rot = cell.rot

            session.flag_export_canvas = True  # this will export an image of the current canvas, when in verbose mode
            session.active_mode.process_grid_change()

            # update slider values
            # TODO: this causes type error when no slider value provided in cspy → provide 0 by default?
            for slider_id in self.sliders.keys():
                if msg['sliders'][slider_id] is not None: self.sliders[slider_id].value = msg['sliders'][slider_id]
                self.sliders[slider_id].process_value()

        except TypeError as t:
            # pass
            print("type error", t)
        except IndexError:
            print("Warning: incoming grid data is incomplete")

    def get_intersection(self, df, x, y):
        # get viewport coordinates of the cell rectangle
        cell_vertices = self.surface.transform(
            [[_x, _y] for _x, _y in [[x, y], [x + 1, y], [x + 1, y + 1], [x, y + 1]]]
        )
        # find elements intersecting with selected cell
        return session._gis.get_intersection_indexer(df, cell_vertices)


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

    def update_cell_data(self, df):
            '''updates every cell's handle and color in grid according to input dataframe (from csv in q100viz/settings folder)'''
            for row in self.grid:
                for cell in row:
                    cell.handle = None
                    df_handle = df.loc[(df['x'] == cell.x) & (df['y'] == cell.y), ['handle']]
                    if not df_handle.empty:
                        cell.handle = df_handle.iloc[0,0]
                    df_color = df.loc[(df['x'] == cell.x) & (df['y'] == cell.y), ['color']]
                    if not df_color.empty and df_color.iloc[0,0]:
                        try:
                            cell.color = pygame.color.Color(df_color.iloc[0,0])
                        except:
                            cell.color = None
class GridCell:
    def __init__(self, x, y, id=-1, rot=-1):
        self.x = x
        self.y = y
        self.id = id
        self.rot = rot
        self.prev_rot = -1
        self.rel_rot = 0
        self.selected = False
        self.color = pygame.color.Color(125, 125, 125)
        self.handle = None  # used to add functionality (e.g. slider controls) to cell, managed by qScope/data/grid_X_setup.csv