''' Input Households Mode: Interact with building-specific parameters using the map '''

import json
import numpy as np
import pygame
import datetime

import q100viz.session as session
from q100viz.settings.config import config
from q100viz.graphics.graphictools import Image
class Buildings_Interaction:
    def __init__(self):
        self.name = 'buildings_interaction'
        self.selection_mode = config['buildings_selection_mode'] # decides how to select intersected buildings. can be 'all' or 'rotation'
        self.previous_connections_selector = ''  # stores the 'global scenario token' that was used to manually set the number of generic connections to heat grid
        self.waiting_to_start = False
        self.mode_token_selection_time = datetime.datetime.now()
        self.activation_buffer_time = 2  # seconds before simulation begins

    def activate(self):
        '''do not call! This function is automatically called in main loop. Instead, enable a mode by setting session.active_mode = session.[mode]'''

        session.environment['mode'] = self.name
        for mode in session.modes:
            mode.waiting_to_start = False

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
        session.api.send_message(json.dumps({'step' : 0}))

    def process_event(self, event):
        if event.type == pygame.locals.MOUSEBUTTONDOWN:
            session.grid_1.mouse_pressed(event.button)
            session.grid_2.mouse_pressed(event.button)

            session.flag_export_canvas = True
            self.process_grid_change()

    def process_grid_change(self):

        session.buildings.df['selected'] = False  # reset buildings
        session.buildings.df['group'] = -1  # reset group

        # reset sliders:
        for grid in session.grid_1, session.grid_2:
            for slider in grid.sliders.values():
                slider.handle = None

        # iterate grid:
        for grid in [session.grid_1, session.grid_2]:
            for y, row in enumerate(grid.grid):
                for x, cell in enumerate(row):
                    if not cell.selected:
                        if cell.handle in session.MODE_SELECTOR_HANDLES:  # interrupt buffer when deselected
                            mode = session.string_to_mode(cell.handle[6:])
                            mode.waiting_to_start = False
                        continue
                    # high performance impact, use sparingly
                    i = grid.get_intersection(session.buildings.df, x, y)

                    # use rotation value to cycle through buildings located in cell
                    if self.selection_mode == 'rotation':
                        n = len(session.buildings.df[i])
                        if n > 0:
                            selection = session.buildings.df[i].iloc[cell.rot % n]
                            session.buildings.df.loc[selection.name,
                                                'selected'] = True  # select cell
                            session.buildings.df.loc[selection.name,
                                                'group'] = cell.id  # pass cell ID to building

                    # select all buildings within range
                    elif self.selection_mode == 'all':
                        for n in range(0, len(session.buildings.df[i])):
                            selection = session.buildings.df[i].iloc[n]
                            session.buildings.df.loc[selection.name,
                                                    'selected'] = True
                            session.buildings.df.loc[selection.name,
                                                'group'] = cell.id  # pass cell ID to building

                    # set slider handles via selected cell:
                    if cell.handle is not None:
                        if cell.handle in session.VALID_DECISION_HANDLES:
                            for slider in grid.sliders.values():
                                if cell.x in range(slider.x_cell_range[0], slider.x_cell_range[1]) and session.active_mode != session.simulation:
                                    slider.update_handle(cell.handle, cell.id)

                        # mode selectors:
                        elif cell.handle in session.MODE_SELECTOR_HANDLES:
                            mode = session.string_to_mode(cell.handle[6:])
                            if not mode.waiting_to_start:
                                self.mode_token_selection_time = datetime.datetime.now()
                                mode.waiting_to_start = True

                        # connect buildings globally:
                        elif cell.handle in ['connections_0', 'connections_20', 'connections_40', 'connections_60', 'connections_80', 'connections_100'] and cell.handle != self.previous_connections_selector:

                            self.previous_connections_selector = cell.handle
                            dec_connections = 0
                            if cell.handle == "connections_20":
                                dec_connections = 0.2
                            elif cell.handle == "connections_40":
                                dec_connections = 0.4
                            elif cell.handle == "connections_60":
                                dec_connections = 0.6
                            elif cell.handle == "connections_80":
                                dec_connections = 0.8
                            elif cell.handle == "connections_100":
                                dec_connections = 1

                            session.environment['scenario_num_connections'] = int(
                                dec_connections * len(session.buildings.df.index))

                            # connect additional buildings as set in scenario:
                            if session.environment['scenario_num_connections'] > 0:
                                # reset:
                                if len(session.scenario_selected_buildings.index) > 0:
                                    session.scenario_selected_buildings['selected'] = False
                                    session.scenario_selected_buildings['connection_to_heat_grid'] = False
                                    session.buildings.df.update(
                                        session.scenario_selected_buildings)

                                # sample data:
                                try:
                                    session.scenario_selected_buildings = session.buildings.df.sample(
                                        n=session.environment['scenario_num_connections'])
                                except Exception as e:
                                    print("max number of possible samples reached. " + str(e))
                                    session.log += "\n%s" % e

                                # filter already selected buildings from list:
                                session.scenario_selected_buildings = session.scenario_selected_buildings[session.scenario_selected_buildings['group'] < 0]
                                for group_df in session.buildings.list_from_groups():
                                    if group_df is not None:
                                        for idx in group_df.index:
                                            if idx in session.scenario_selected_buildings.index:
                                                session.scenario_selected_buildings = session.scenario_selected_buildings.drop(idx)

                                # select and connect sampled buildings:
                                session.scenario_selected_buildings['selected'] = True
                                session.scenario_selected_buildings['connection_to_heat_grid'] = 2020
                                print("selecting random {0} buildings:".format(
                                    session.environment['scenario_num_connections']))
                                session.buildings.df.update(
                                session.scenario_selected_buildings)

                            else:  # value is 0: deselect all
                                session.scenario_selected_buildings['selected'] = False
                                session.scenario_selected_buildings['connection_to_heat_grid'] = False
                                session.buildings.df.update(
                                session.scenario_selected_buildings)
                                session.scenario_selected_buildings = session.scenario_selected_buildings[0:0] # empty dataframe

        session.api.send_message(json.dumps(session.environment))
        session.api.send_message(json.dumps(session.buildings.get_dict_with_api_wrapper()))

    def draw(self, canvas):

        try:
            # highlight selected buildings (draws colored stroke on top)
            if len(session.buildings.df[session.buildings.df.selected]):

                sel_buildings = session.buildings.df[(session.buildings.df.selected)]
                for building in sel_buildings.to_dict('records'):
                    fill_color = pygame.Color(session.user_colors[int(building['group'])])

                    points = session._gis.surface.transform(building['geometry'].exterior.coords)
                    pygame.draw.polygon(session._gis.surface, fill_color, points, 2)

            # coloring slider area:
            for slider_dict in session.grid_1.sliders, session.grid_2.sliders:
                for slider in slider_dict.values():
                    slider.draw_area()

        except Exception as e:
                print("Cannot draw frontend:", e)
                session.log += "\nCannot draw frontend: %s" % e

        font = pygame.font.SysFont('Arial', 18)
        nrows = 22

        column = 18
        y = 1*22
        canvas.blit(font.render("Anschlüsse", True, pygame.Color(255,255,255)), session.grid_2.rects_transformed[column+y][1][0])

        # draw num connections:
        i = 1
        for num_string in ["0%", "20%", "40%", "60%", "80%", "100%"]:
            column = nrows * 1 + 18
            canvas.blit(font.render(num_string, True, pygame.Color(255,255,255)), session.grid_2.rects_transformed[column+nrows*i][1][0])
            i += 1

        column = 16
        row = 11
        canvas.blit(font.render(
            "Quartiersdaten", True, pygame.Color(255,255,255)),
            (session.grid_2.rects_transformed[column+nrows*row][1][0][0] + 5,  # x
            session.grid_2.rects_transformed[column+nrows*row][1][0][1] + 12)  # y
        )

        column = 16
        row = 13
        font = pygame.font.SysFont('Arial', 18)
        canvas.blit(font.render(
            "Individualdaten", True, pygame.Color(255,255,255)),
            (session.grid_2.rects_transformed[column+nrows*row][1][0][0] + 5,
             session.grid_2.rects_transformed[column+nrows*row][1][0][1] + 10)
        )

        column = 17
        row = 15
        font = pygame.font.SysFont('Arial', 18)
        canvas.blit(font.render(
            "Simulation", True, pygame.Color(255,255,255)),
            (session.grid_2.rects_transformed[column+nrows*row][1][0][0] + 5,
            session.grid_2.rects_transformed[column+nrows*row][1][0][1] + 10)
        )

        # draw mode buffer:
        column = 20
        for mode, row in zip(session.modes, [18, 16, 14, 12]):
            if mode.waiting_to_start:
                sim_string = str(round(mode.activation_buffer_time -(datetime.datetime.now() - self.mode_token_selection_time).total_seconds(), 2))
                canvas.blit(font.render(sim_string, True, pygame.Color(255,255,255)), session.grid_2.rects_transformed[column+nrows*row][1][0])

    def update(self):
        for mode in session.modes:
            if mode.waiting_to_start:
                if (datetime.datetime.now() - self.mode_token_selection_time).total_seconds() > mode.activation_buffer_time and (datetime.datetime.now() - self.mode_token_selection_time).total_seconds() < 10:
                    for mode_ in session.modes:
                        mode_.waiting_to_start = False

                    if mode is session.simulation:
                        session.simulation.setup()
                    session.active_mode = mode  # marks simulation to be started in main thread
