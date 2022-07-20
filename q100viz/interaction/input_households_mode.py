''' Input Households Mode: Interact with building-specific parameters using the map '''

import pandas as pd
import pygame

import q100viz.session as session
class Input_Households:
    def __init__(self):
        self.name = 'input_households'

    def activate(self):
        session.active_handler = session.handlers['input_households']
        session.environment['mode'] = self.name

        # graphics:
        session.show_polygons = True
        session.show_basemap = True
        session.flag_export_canvas = True  # export "empty" polygon layer once

        # sliders:
        for slider in session.grid_1.slider, session.grid_2.slider:
            slider.show_text = True
            slider.show_controls = True

        # setup mode selectors:
        session.grid_1.update_cell_data(session.input_households_grid_1)
        session.grid_2.update_cell_data(session.input_households_grid_2)

        # send data:
        session.api.send_df_with_session_env(None)

    def process_event(self, event):
        if event.type == pygame.locals.MOUSEBUTTONDOWN:
            session.grid_1.mouse_pressed(event.button)
            session.grid_2.mouse_pressed(event.button)

            session.flag_export_canvas = True
            self.process_grid_change()

    def process_grid_change(self):

        session.buildings['selected'] = False  # reset buildings
        session.buildings['group'] = -1  # reset group
        session.buildings_groups = ['' for i in range(session.num_of_users)] # reset groups

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
                                                  'selected'] = True  # select cell
                            session.buildings.loc[selection.name,
                                                  'group'] = cell.id  # pass cell ID to building

                        # set slider handles via selected cell in last row:
                        if cell.handle is not None:
                            if cell.handle in ['connection_to_heat_grid', 'electricity_supplier', 'refurbished', 'environmental_engagement']:
                                if grid.slider.show_controls:
                                    grid.slider.handle = cell.handle
                                    grid.slider.id = cell.id
                                    if grid.slider.previous_handle is not grid.slider.handle:
                                        session.print_verbose(
                                            "slider id: {0}, handle: {1}".format(str(grid.slider.id), str(grid.slider.handle)))
                                        grid.slider.previous_handle = grid.slider.handle

                            elif cell.handle == 'start_input_scenarios':
                                session.handlers['input_scenarios'].activate()

                            elif cell.handle == 'start_simulation':
                                session.handlers['simulation'].activate()

        session.api.send_grouped_buildings()

    def draw(self, canvas):

        try:
            if len(session.buildings[session.buildings.selected]):
                # highlight selected buildings
                session.gis.draw_polygon_layer(
                    canvas,
                    session.buildings[session.buildings.selected], 2, (255, 0, 127)
                )

            # coloring slider area:
            for slider in session.grid_1.slider, session.grid_2.slider:
                slider.draw_area()

        except Exception as e:
                session.log += "\n%s" % e


    def update(self):
        pass

def get_intersection(df, grid, x, y):
    # get viewport coordinates of the cell rectangle
    cell_vertices = grid.surface.transform(
        [[_x, _y] for _x, _y in [[x, y], [x + 1, y], [x + 1, y + 1], [x, y + 1]]]
    )
    # find elements intersecting with selected cell
    return session.gis.get_intersection_indexer(df, cell_vertices)
