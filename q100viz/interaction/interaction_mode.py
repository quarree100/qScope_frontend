''' Input Households Mode: Interact with building-specific parameters using the map '''

import json
import pygame

import q100viz.session as session
from q100viz.settings.config import config
class Buildings_Interaction:
    def __init__(self):
        self.name = 'buildings_interaction'
        self.selection_mode = config['buildings_selection_mode'] # decides how to select intersected buildings. can be 'all' or 'rotation'

    def activate(self):
        session.active_handler = session.handlers['buildings_interaction']
        session.environment['mode'] = self.name

        # graphics:
        session.show_polygons = True
        session.show_basemap = True
        session.flag_export_canvas = True  # export "empty" polygon layer once

        # sliders:
        for grid in session.grid_1, session.grid_2:
            for slider in grid.sliders.values():
                slider.show_text = True
                slider.show_controls = True

        # setup mode selectors:
        session.grid_1.update_cell_data(session.buildings_interaction_grid_1)
        session.grid_2.update_cell_data(session.buildings_interaction_grid_2)

        # send data:
        session.api.send_df_with_session_env(None)

    def process_event(self, event):
        if event.type == pygame.locals.MOUSEBUTTONDOWN:
            session.grid_1.mouse_pressed(event.button)
            session.grid_2.mouse_pressed(event.button)

            session.flag_export_canvas = True
            self.process_grid_change()

    def process_grid_change(self):

        session.buildings_df['selected'] = False  # reset buildings
        session.buildings_df['group'] = -1  # reset group
        session.buildings_groups_list = [None for i in range(session.num_of_users)] # reset groups

        for grid in [session.grid_1, session.grid_2]:
            for y, row in enumerate(grid.grid):
                for x, cell in enumerate(row):
                    if cell.selected:
                        # high performance impact, use sparingly
                        i = get_intersection(session.buildings_df, grid, x, y)

                        # use rotation value to cycle through buildings located in cell
                        if self.selection_mode == 'rotation':
                            n = len(session.buildings_df[i])
                            if n > 0:
                                selection = session.buildings_df[i].iloc[cell.rot % n]
                                session.buildings_df.loc[selection.name,
                                                    'selected'] = True  # select cell
                                session.buildings_df.loc[selection.name,
                                                    'group'] = cell.id  # pass cell ID to building

                        # select all buildings within range
                        elif self.selection_mode == 'all':
                            for n in range(0, len(session.buildings_df[i])):
                                selection = session.buildings_df[i].iloc[n]
                                session.buildings_df.loc[selection.name,
                                                        'selected'] = True
                                session.buildings_df.loc[selection.name,
                                                    'group'] = cell.id  # pass cell ID to building

                        # set slider handles via selected cell in last row:
                        if cell.handle is not None:
                            if cell.handle in session.VALID_GRID_HANDLES:
                                for slider in grid.sliders.values():
                                    if cell.x in range(slider.x_cell_range[0], slider.x_cell_range[1]):
                                        slider.update_handle(cell.handle, cell.id)

                            elif cell.handle == 'start_input_scenarios':
                                session.handlers['input_scenarios'].activate()

                            elif cell.handle == 'start_simulation':
                                session.handlers['simulation'].activate()

        session.api.send_message(json.dumps(session.api.make_buildings_groups_dict()))

        print(session.buildings_groups_list)

    def draw(self, canvas):

        try:
            # highlight selected buildings (draws colored stroke on top)
            if len(session.buildings_df[session.buildings_df.selected]):
                session.gis.draw_polygon_layer(
                    canvas,
                    session.buildings_df[session.buildings_df.selected], 2, (255, 0, 127)
                )

            # coloring slider area:
            for slider_dict in session.grid_1.sliders, session.grid_2.sliders:
                for slider in slider_dict.values():
                    slider.draw_area()

        except Exception as e:
                print(e)
                session.log += "\nCannot draw slider: %s" % e


    def update(self):
        pass

def get_intersection(df, grid, x, y):
    # get viewport coordinates of the cell rectangle
    cell_vertices = grid.surface.transform(
        [[_x, _y] for _x, _y in [[x, y], [x + 1, y], [x + 1, y + 1], [x, y + 1]]]
    )
    # find elements intersecting with selected cell
    return session.gis.get_intersection_indexer(df, cell_vertices)
