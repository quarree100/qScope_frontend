''' Input Households Mode: Interact with building-specific parameters using the map '''

import json
import shapely
import pygame
import datetime

import q100viz.session as session
from q100viz.devtools import devtools
from q100viz.settings.config import config

class Buildings_Interaction:
    def __init__(self):
        self.name = 'buildings_interaction'
        # stores the 'global scenario token' that was used to manually set the number of generic connections to heat grid
        self.previous_connections_selector = ''
        self.mode_token_selection_time = datetime.datetime.now()
        self.activation_buffer_time = 2  # seconds before simulation begins

    def activate(self):
        '''do not call! This function is automatically called in main loop. Instead, enable a mode by setting session.active_mode = session.[mode]'''

        session.environment['mode'] = self.name
        session.pending_mode = None

        # graphics:
        session.show_polygons = True
        session.show_basemap = True
        session.flag_export_canvas = True  # export "empty" polygon layer once

        # sliders:
        for slider in session.sliders:
            slider.show_text = True
            slider.show_controls = True

        # setup mode selectors:
        # TODO: session.grid_1.update_cell_data(session.buildings_interaction_grid_1)
        # session.grid_2.update_cell_data(session.buildings_interaction_grid_2)

        # send data:
        session.api.send_df_with_session_env(None)
        session.api.send_message(json.dumps({'step': 0}))

    def process_event(self, event):
        pass

    def process_grid_change(self):

        return

        session.buildings.df['selected'] = False  # reset buildings
        session.buildings.df['group'] = -1  # reset group

        # iterate grid:
        # TODO: change mode:
        mode = session.string_to_mode(cell.handle[6:])
        session.pending_mode = None

        # TODO: Slider handling

        if True:

            if cell.handle in session.VALID_DECISION_HANDLES:
                for slider in grid.sliders.values():
                    if cell.x in range(slider.x_cell_range[0], slider.x_cell_range[1]):
                        slider.update_handle(cell.handle, cell.id)

            # mode selectors:
            elif cell.handle in session.MODE_SELECTOR_HANDLES:
                mode = session.string_to_mode(cell.handle[6:])
                if not mode == session.pending_mode:
                    self.mode_token_selection_time = datetime.datetime.now()
                    session.pending_mode = mode

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
                        devtools.log += "\n%s" % e

                    # filter already selected buildings from list:
                    session.scenario_selected_buildings = session.scenario_selected_buildings[
                        session.scenario_selected_buildings['group'] < 0]
                    for group_df in session.buildings.list_from_groups():
                        if group_df is not None:
                            for idx in group_df.index:
                                if idx in session.scenario_selected_buildings.index:
                                    session.scenario_selected_buildings = session.scenario_selected_buildings.drop(
                                        idx)

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
                    # empty dataframe
                    session.scenario_selected_buildings = session.scenario_selected_buildings[
                        0:0]

        session.api.send_message(json.dumps(session.environment))
        session.api.send_message(json.dumps(
            session.buildings.get_dict_with_api_wrapper()))

    def draw(self, canvas):

        try:
            # highlight selected buildings (draws colored stroke on top)
            if len(session.buildings.df[session.buildings.df.selected]):

                sel_buildings = session.buildings.df[(
                    session.buildings.df.selected)]
                for building in sel_buildings.to_dict('records'):
                    fill_color = pygame.Color(
                        session.user_colors[int(building['group'])])

                    points = session._gis.surface.transform(
                        building['geometry'].exterior.coords)
                    pygame.draw.polygon(
                        session._gis.surface, fill_color, points, 2)

            # coloring slider area:
            for slider in session.sliders:
                slider.draw_area()

        except Exception as e:
            print("Cannot draw frontend:", e)
            devtools.log += "\nCannot draw frontend: %s" % e

        # ------------------------- TEXT DISPLAY ----------------------

        font = pygame.font.SysFont('Arial', 24)

        x = config["CANVAS_SIZE"][0] * 0.855
        y = config["CANVAS_SIZE"][1] * 0.1
        line_height = 50

        # global settings:
        canvas.blit(font.render("Anschlüsse", True,
                    pygame.Color(255, 255, 255)), (x, y))

        # draw num connections:
        i = 1
        for num_string in ["0%", "20%", "40%", "60%", "80%", "100%"]:
            canvas.blit(font.render(num_string, True, pygame.Color(
                255, 255, 255)), (x, y + line_height * i))
            i += 1

        i += 1
        canvas.blit(font.render(
            "Quartiersdaten", True, pygame.Color(255, 255, 255)), (x, y + i * line_height))

        font = pygame.font.SysFont('Arial', 18)
        i += 1
        canvas.blit(font.render(
            "Individualdaten", True, pygame.Color(255, 255, 255)),
            (x, y + i * line_height)
        )

        return
        column = 17
        row = 15
        font = pygame.font.SysFont('Arial', 18)
        canvas.blit(font.render(
            "Simulation", True, pygame.Color(255, 255, 255)),
            (session.grid_2.rects_transformed[column+nrows*row][1][0][0] + 5,
             session.grid_2.rects_transformed[column+nrows*row][1][0][1] + 10)
        )

        # draw mode buffer:
        column = 20
        if session.pending_mode is not None:
            sim_string = str(round(session.pending_mode.activation_buffer_time - (
                datetime.datetime.now() - self.mode_token_selection_time).total_seconds(), 2))
            canvas.blit(font.render(sim_string, True, pygame.Color(255, 255, 255)), (
                session.grid_2.rects_transformed[column+nrows*row][1][0][0], session.grid_2.rects_transformed[column+nrows*row][1][0][1] + 40))

    def update(self):
        if session.pending_mode is None:
            return

        if (datetime.datetime.now() - self.mode_token_selection_time).total_seconds() > session.pending_mode.activation_buffer_time and (datetime.datetime.now() - self.mode_token_selection_time).total_seconds() < 10:
            # marks simulation to be started in main thread
            session.active_mode = session.pending_mode
            session.pending_mode = None
            self.mode_token_selection_time = datetime.datetime.now()

            if session.active_mode is session.simulation:
                session.simulation.setup()
