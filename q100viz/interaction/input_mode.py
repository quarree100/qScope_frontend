''' The Input Mode displays everything needed for standard User Interaction '''

import pygame

import q100viz.keystone as keystone
import q100viz.session as session
from config import config


class InputMode:
    def __init__(self):
        pass

    def process_event(self, event, config):
        if event.type == pygame.locals.MOUSEBUTTONDOWN:
            session.grid_1.mouse_pressed(event.button)
            session.grid_2.mouse_pressed(event.button)
            session.print_verbose(session.buildings)
            session.flag_export_canvas = True

        session.buildings['selected'] = False

        # process grid changes
        for grid in [session.grid_1, session.grid_2]:
            for y, row in enumerate(grid.grid):
                for x, cell in enumerate(row):
                    if cell.selected:
                        # high performance impact, use sparingly
                        i = get_intersection(session.buildings, grid, x, y)

                        # use rotation value to cycle through buildings located in cell
                        n = len(session.buildings[i])
                        if n > 0:
                            selection = session.buildings[i].iloc[cell.rot % n]
                            session.buildings.loc[selection.name,
                                                  'selected'] = True

                        # set slider handles via selected cell in last row:
                        if y == len(grid.grid)-1:
                            if x < session.grid_settings['ncols'] / 2:
                                grid.slider.handle = session.slider_handles[
                                    int(x / session.grid_settings['ncols'] * len(session.slider_handles))]
                                if grid.slider.previous_handle is not grid.slider.handle:
                                    session.print_verbose(
                                        ("slider_handle: ", grid.slider.handle))
                                    grid.slider.previous_handle = grid.slider.handle

                            # enter simulation mode:
                            elif x == int(session.grid_settings['ncols'] * 2 / 3 + 2):
                                session.active_handler = session.handlers['simulation']
                                grid.deselect(int(session.grid_settings['ncols'] * 2 / 3), len(grid.grid) - 1)
                                print(session.active_handler)


    def draw(self, canvas):

        if len(session.buildings[session.buildings.selected]):
            # highlight selected buildings
            session.gis.draw_polygon_layer(
                canvas,
                session.buildings[session.buildings.selected], 2, (255, 0, 127)
            )

    def update(self):
        pass

def get_intersection(df, grid, x, y):
    # get viewport coordinates of the cell rectangle
    cell_vertices = grid.surface.transform(
        [[_x, _y] for _x, _y in [[x, y], [x + 1, y], [x + 1, y + 1], [x, y + 1]]]
    )
    # find elements intersecting with selected cell
    return session.gis.get_intersection_indexer(df, cell_vertices)