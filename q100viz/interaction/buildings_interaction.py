''' Input Households Mode: Interact with building-specific parameters using the map '''

import json
import shapely
import pygame
import datetime

import q100viz.session as session
from q100viz.devtools import devtools
from q100viz.settings.config import config
from q100viz.interaction.PopupMenu import TouchMenu


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
        session.api.send_dict(session.environment)
        session.api.send_message(json.dumps({'step': 0}))

    def process_event(self, event):
        if event.type != pygame.locals.MOUSEBUTTONDOWN:
            return

        mouse_pos = pygame.mouse.get_pos()

        buildings = session.buildings.df

        # 1. check popup hits:
        for popup in [p for p in buildings['popup'] if p]:
            if popup.handle_mouse_button(mouse_pos): return

        # 2. check building hits:
        for idx, row in enumerate(buildings.index):
            if shapely.Point(mouse_pos).within(shapely.geometry.Polygon(buildings.loc[idx, 'polygon'])):

                if not any(session.group_available):
                    # deselect and return:
                    buildings.at[idx, 'popup'] = None
                    if idx in session.popup_menus.keys():
                        del session.popup_menus[idx]    
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
                        popup = TouchMenu(
                            session.viewport,
                            centroid,
                            displace=(0, 200),
                            idx=idx
                        )

                else:  # deselect
                    buildings.at[idx, 'popup'].destroy()
                    if buildings.loc[idx, 'group'] >= 0:
                        # make group available again
                        session.group_available[buildings.loc[idx,'group']] = True
                    buildings.at[idx, 'group'] = -1

        # session.api.send_message(json.dumps(session.environment))
        # session.api.send_message(json.dumps(
        #     session.buildings.get_dict_with_api_wrapper()))

    def process_grid_change(self):

        return

    def draw(self, canvas):

        # draw GIS layers:
        if session.show_polygons:
            session._gis.draw_linestring_layer(
                canvas, session._gis.nahwaermenetz, (217, 9, 9), 3)
            session._gis.draw_buildings_connections(
                session.buildings.df)  # draw lines to closest heat grid
            
            # fill interactive:
            session._gis.draw_polygon_layer_bool(
                surface=canvas, 
                df=session.buildings.df, stroke=0,
                fill_false=session.global_colors['interactive'],
                fill_attr='connection_to_heat_grid')

            # stroke according to connection status:
            session._gis.draw_polygon_layer_bool(
                surface=canvas, df=session.buildings.df,
                stroke=1,
                fill_false=(0,0,0),
                fill_attr='connection_to_heat_grid')

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

        for popup in session.popup_menus.values():
            popup.draw()
