''' Input Households Mode: Interact with building-specific parameters using the map '''

import json
import random
import pygame
import datetime

import q100viz.session as session
from q100viz.settings.config import config
class Buildings_Interaction:
    def __init__(self):
        self.name = 'buildings_interaction'
        self.selection_mode = config['buildings_selection_mode'] # decides how to select intersected buildings. can be 'all' or 'rotation'
        self.previous_connections_selector = ''
        self.waiting_for_simulation = False
        self.sim_token_selection_time = datetime.datetime.now()
        self.activation_buffer_time = 4  # seconds before simulation begins

    def activate(self):
        '''do not call! This function is automatically called in main loop. Instead, enable a mode by setting session.active_mode = session.[mode]'''

        session.active_mode = self
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
                    if cell.selected:
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
                            if cell.handle in session.VALID_GRID_HANDLES:
                                for slider in grid.sliders.values():
                                    if cell.x in range(slider.x_cell_range[0], slider.x_cell_range[1]):
                                        slider.update_handle(cell.handle, cell.id)

                            elif cell.handle == 'start_individual_data_view':
                                session.active_mode = session.individual_data_view

                            elif cell.handle == 'start_total_data_view':
                                session.active_mode = session.total_data_view

                            elif cell.handle == 'start_simulation':
                                if not self.waiting_for_simulation:
                                    self.sim_token_selection_time = datetime.datetime.now()
                                    self.waiting_for_simulation = True
                                print(self.waiting_for_simulation)

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

                                    # drop already selected buildings from list:
                                    for buildings_group in session.buildings.list_from_groups():
                                        for idx in buildings_group.index:
                                            if idx in session.scenario_selected_buildings.index:
                                                session.scenario_selected_buildings = session.scenario_selected_buildings.drop(idx)

                                    # select and connect sampled buildings:
                                    session.scenario_selected_buildings['selected'] = True
                                    session.scenario_selected_buildings['connection_to_heat_grid'] = random.randint(2020, session.simulation.max_year)
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

                        print(session.environment['scenario_num_connections'], len(session.scenario_selected_buildings))


                    elif cell.handle == 'start_simulation':  # cell not selected
                        self.waiting_for_simulation = False

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

        canvas.blit(font.render(
            "Quartiersdaten", True, pygame.Color(255,255,255)),
            (session.grid_2.rects_transformed[20*14][1][0][0] + 5,  # x
            session.grid_2.rects_transformed[20*14][1][0][1] + 12)  # y
        )

        column = 16
        row = 14
        font = pygame.font.SysFont('Arial', 18)
        canvas.blit(font.render(
            "Individualdaten", True, pygame.Color(255,255,255)),
            (session.grid_2.rects_transformed[column+nrows*row][1][0][0] + 5,
             session.grid_2.rects_transformed[column+nrows*row][1][0][1] + 10)
        )

        if self.waiting_for_simulation:
            sim_string = str(round(session.simulation.activation_buffer_time -(datetime.datetime.now() - self.sim_token_selection_time).total_seconds(), 2))
            canvas.blit(font.render(sim_string, True, pygame.Color(255,255,255)), session.grid_2.rects_transformed[20+22*17][1][0])

        column = 17
        row = 16
        font = pygame.font.SysFont('Arial', 18)
        canvas.blit(font.render(
            "Simulation", True, pygame.Color(255,255,255)),
            (session.grid_2.rects_transformed[column+nrows*row][1][0][0] + 5,
            session.grid_2.rects_transformed[column+nrows*row][1][0][1] + 10)
        )

    def update(self):
        if self.waiting_for_simulation and not session.simulation.running:
            if (datetime.datetime.now() - self.sim_token_selection_time).total_seconds() > session.simulation.activation_buffer_time:
                self.waiting_for_simulation = False

                session.simulation.setup()
                session.active_mode = session.simulation  # marks simulation to be started in main thread
