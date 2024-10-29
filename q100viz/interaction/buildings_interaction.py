''' Input Households Mode: Interact with building-specific parameters using the map '''

import json
import shapely
import pygame
import datetime

import q100viz.session as session
from q100viz.devtools import devtools
from q100viz.settings.config import config
from q100viz.interaction.PopupMenu import PopupMenu


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

        # send data:
        session.api.send_df_with_session_env(None)
        session.api.send_message(json.dumps({'step': 0}))

    def process_event(self, event):
        if event.type != pygame.locals.MOUSEBUTTONDOWN:
            return

        mouse_pos = pygame.mouse.get_pos()

        buildings = session.buildings.df

        # 1. check popup hits:
        for popup in [p for p in buildings['popup'] if p]:
            if popup.bounding_box.collidepoint(mouse_pos):
                popup.handle_mouse_button(mouse_pos)
                return

        # 2. check building hits:
        for idx, row in enumerate(buildings.index):
            if shapely.Point(mouse_pos).within(shapely.geometry.Polygon(buildings.loc[idx, 'polygon'])):

                if not any(session.group_available):
                    # deselect and return:
                    buildings.at[idx, 'popup'] = None
                    buildings.at[idx, 'selected'] = False
                    if buildings.loc[idx, 'group'] >= 0:
                        # make group available again
                        session.group_available[buildings.loc[idx,
                                                              'group']] = True
                    buildings.at[idx, 'group'] = -1
                    return

                # toggle selection:
                buildings.at[idx,
                             'selected'] = not buildings.loc[idx, 'selected']

                if buildings.loc[idx, 'selected']:

                    if any(session.group_available):
                        # add to arbitrary group:
                        group_available = None
                        for i in range(session.num_of_users):
                            if session.group_available[i] == True:
                                session.group_available[i] = False
                                group_available = i
                                break
                        buildings.at[idx, 'group'] = group_available

                        # create popup menu:
                        centroid = shapely.geometry.Polygon(
                            buildings.loc[idx, 'polygon']).centroid.coords[0]
                        popup = PopupMenu(
                            session.viewport,
                            centroid,
                            displace=(0, 200),
                            idx=idx
                        )
                        buildings.at[idx, 'popup'] = popup
                        session.popup_menus[idx] = popup

                else:  # deselect
                    buildings.at[idx, 'popup'] = None
                    del session.popup_menus[idx]
                    if buildings.loc[idx, 'group'] >= 0:
                        # make group available again
                        session.group_available[buildings.loc[idx,'group']] = True
                    buildings.at[idx, 'group'] = -1

        # session.api.send_message(json.dumps(session.environment))
        # session.api.send_message(json.dumps(
        #     session.buildings.get_dict_with_api_wrapper()))

    def process_grid_change(self):

        return

        session.buildings.df['selected'] = False  # reset buildings
        session.buildings.df['group'] = -1  # reset group

        # iterate grid:
        # TODO: change mode:
        mode = session.modes[cell.handle[6:]]
        session.pending_mode = None

        # TODO: Slider handling

        if True:

            if cell.handle in session.VALID_DECISION_HANDLES:
                for slider in grid.sliders.values():
                    if cell.x in range(slider.x_cell_range[0], slider.x_cell_range[1]):
                        slider.update_handle(cell.handle, cell.id)

            # mode selectors:
            elif cell.handle in session.MODE_SELECTOR_HANDLES:
                mode = session.modes[cell.handle[6:]]
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

    def draw(self, canvas):

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

    def update(self):
        if session.pending_mode is None:
            return

        if (datetime.datetime.now() - self.mode_token_selection_time).total_seconds() > session.pending_mode.activation_buffer_time and (datetime.datetime.now() - self.mode_token_selection_time).total_seconds() < 10:
            # marks simulation to be started in main thread
            session.active_mode = session.pending_mode
            session.pending_mode = None
            self.mode_token_selection_time = datetime.datetime.now()

            if session.active_mode is session.modes['simulation']:
                session.modes['simulation'].setup()
