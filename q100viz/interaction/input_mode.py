''' The Input Mode displays everything needed for standard User Interaction '''

import pygame
import pandas as pd

import q100viz.keystone as keystone
import q100viz.session as session
import q100viz.stats as stats
from config import config
class InputMode:
    def __init__(self):
        self.name = 'input_households'

    def activate(self):
        session.show_polygons = True
        session.show_basemap = True
        session.active_handler = session.handlers['input_households']
        session.environment['mode'] = self.name

        # sliders:
        for slider in session.grid_1.slider, session.grid_2.slider:
            slider.show_text = True
            slider.show_controls = True

        # setup mode selectors:
        session.grid_1.update_cell_data(session.input_households_grid_1)
        session.grid_2.update_cell_data(session.input_households_grid_2)

        # send data:
        session.stats.send_dataframe_with_environment_variables(None, session.environment)

    def process_event(self, event):
            if event.type == pygame.locals.MOUSEBUTTONDOWN:
                session.grid_1.mouse_pressed(event.button)
                session.grid_2.mouse_pressed(event.button)

                session.flag_export_canvas = True
                self.process_grid_change()

    def process_grid_change(self):
        session.buildings['selected'] = False
        for grid in [session.grid_1, session.grid_2]:
            for y, row in enumerate(grid.grid):
                for x, cell in enumerate(row):
                    if cell.selected:
                        # print(cell.x, cell.y, cell.handle)
                        # high performance impact, use sparingly
                        i = get_intersection(session.buildings, grid, x, y)

                        # use rotation value to cycle through buildings located in cell
                        n = len(session.buildings[i])
                        if n > 0:
                            selection = session.buildings[i].iloc[cell.rot % n]
                            session.buildings.loc[selection.name,
                                                'selected'] = True

                        # set slider handles via selected cell in last row:
                        if cell.handle is not None:
                            if cell.handle in ['connection_to_heat_grid', 'electricity_supplier', 'refurbished', 'environmental_engagement']:
                                # grid.slider.handle = cell.handle
                                session.grid_2.slider.handle = cell.handle
                                if grid.slider.previous_handle is not grid.slider.handle:
                                    session.print_verbose(
                                        ("slider_handle: ", grid.slider.handle))
                                    grid.slider.previous_handle = grid.slider.handle

                            elif cell.handle == 'start_input_environment':
                                session.handlers['input_environment'].activate()

        session.stats.send_simplified_dataframe_with_environment_variables(session.buildings[session.buildings.selected], session.environment)

    def draw(self, canvas):

        if len(session.buildings[session.buildings.selected]):
            # highlight selected buildings
            session.gis.draw_polygon_layer(
                canvas,
                session.buildings[session.buildings.selected], 2, (255, 0, 127)
            )

        # coloring slider area:
        for slider in session.grid_1.slider, session.grid_2.slider:
            slider.draw_area()

    def update(self):
        pass

def get_intersection(df, grid, x, y):
    # get viewport coordinates of the cell rectangle
    cell_vertices = grid.surface.transform(
        [[_x, _y] for _x, _y in [[x, y], [x + 1, y], [x + 1, y + 1], [x, y + 1]]]
    )
    # find elements intersecting with selected cell
    return session.gis.get_intersection_indexer(df, cell_vertices)


class Input_Environment:
    def __init__(self):
        self.name = 'input_environment'

    def activate(self):
        session.show_polygons = True
        session.show_basemap = True
        session.active_handler = session.handlers['input_environment']
        session.environment['mode'] = self.name

        # sliders:
        for slider in session.grid_1.slider, session.grid_2.slider:
            slider.show_text = True
            slider.show_controls = True

        # setup mode selectors:
        session.grid_1.update_cell_data(session.input_environment_grid_1)
        session.grid_2.update_cell_data(session.input_environment_grid_2)

        # send data:
        session.stats.send_dataframe_with_environment_variables(None, session.environment)

    def process_event(self, event):
            if event.type == pygame.locals.MOUSEBUTTONDOWN:
                session.grid_1.mouse_pressed(event.button)
                session.grid_2.mouse_pressed(event.button)

                session.flag_export_canvas = True
                self.process_grid_change()

    def process_grid_change(self):
        session.buildings['selected'] = False
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
                        if cell.handle is not None:
                            if cell.handle in cell.handle in ['connection_to_heat_grid', 'electricity_supplier', 'refurbished', 'environmental_engagement']:
                                grid.slider.handle = cell.handle
                                if grid.slider.previous_handle is not grid.slider.handle:
                                    session.print_verbose(
                                        ("slider_handle: ", grid.slider.handle))
                                    grid.slider.previous_handle = grid.slider.handle

                            elif cell.handle == 'start_input_households':
                                session.handlers['input_households'].activate()

        session.stats.send_simplified_dataframe_with_environment_variables(session.buildings[session.buildings.selected], session.environment)

    def draw(self, canvas):

        if len(session.buildings[session.buildings.selected]):
            # highlight selected buildings
            session.gis.draw_polygon_layer(
                canvas,
                session.buildings[session.buildings.selected], 2, (255, 0, 127)
            )

        # coloring slider area:
        for slider in session.grid_1.slider, session.grid_2.slider:
            slider.draw_area()

    def update(self):
        pass