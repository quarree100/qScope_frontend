''' Input Households Mode: Interact with building-specific parameters using the map '''

import json
import shapely
import pygame
import datetime

import q100viz.session as session
from q100viz.devtools import devtools
from q100viz.settings.config import config
from q100viz.interaction.PopupMenu import *


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
        session.api.push_message(json.dumps({'step': 0}))

    def process_event(self, event_pos):

        buildings = session.buildings.df

        for popup in [p for p in list(session.popup_menus.values()) if p]:
            if popup.handle_mouse_button(event_pos): return
                    
    def process_tangible_event(self, tangible_id, pos, rotation):
        buildings = session.buildings.df
        
        # check collision with decision icons:
        for popup in [p for p in list(session.popup_menus.values()) if p]:
            if popup.radius is not popup.target_radius: return  # animation not complete
            for key in session.VALID_DECISION_HANDLES:
                
                if popup.icons[key].selected: continue
                if popup.icons[key].rect.collidepoint(pos):  # TODO: rect could be defined more precisely as the circle, that it is.
                    popup.handle_mouse_button(pos)
                    session.popup_menus[tangible_id] = \
                    TangibleDecisionMenu(
                        session.viewport,
                        pos,
                        displace=(0, 200),
                        start_rotation=rotation,
                        building_idx=popup.building_idx,
                        tangible_id=tangible_id,
                        parent = popup,
                        slider_handle = key
                    )
                    return

        # leave building:
        if tangible_id in list(buildings['tangible'].values):
            bd = buildings[buildings['tangible'] == tangible_id]
            if not shapely.Point(pos).within(shapely.geometry.Polygon(bd.loc[bd.index[0], 'polygon'])):
                session.buildings.df.loc[session.buildings.df['tangible'] == tangible_id, 'tangible'] = None

                if session.popup_menus[tangible_id]:
                    session.popup_menus[tangible_id].destroy_me = True
                session.api.send_message_as_json(session.buildings.get_dict_with_api_wrapper())
                return  # tangible not on building anymore
            else:
                return  # tangible still on building
        
        # return if tangible has a popup already:
        if tangible_id in session.popup_menus.keys():
            if session.popup_menus[tangible_id] is not None: return
        # allow only one building per user:
        for i, row in session.buildings.df[session.buildings.df['group'] == tangible_id % session.num_of_users].iterrows():
            if row['tangible'] is not None: return
                
        # building selection:
        for idx in buildings[buildings['group'] == -1].index:
            # new building selected:
            if shapely.Point(pos).within(shapely.geometry.Polygon(buildings.loc[idx, 'polygon'])):
                # deselect all others:
                buildings.loc[buildings['group'] == tangible_id % session.num_of_users, 'selected'] = False
                buildings.loc[buildings['group'] == tangible_id % session.num_of_users, 'group'] = -1

                buildings.at[idx, 'tangible'] = tangible_id
                buildings.at[idx, 'selected'] = True
                buildings.at[idx, 'group'] = tangible_id % session.num_of_users
                session.popup_menus[tangible_id] = \
                    TangibleMenu(
                    session.viewport,
                    pos,
                    displace=(0, 200),
                    building_idx=idx,
                    start_rotation=rotation,
                    tangible_id=tangible_id
                )
                session.api.send_message_as_json(session.buildings.get_dict_with_api_wrapper())

                return

    def draw(self, canvas):

        # draw GIS layers:
        if session.show_polygons:
            session._gis.draw_linestring_layer(
                canvas, session._gis.nahwaermenetz, (217, 9, 9), 3)
            
            # fill interactive:
            session._gis.draw_polygon_layer(
                surface=canvas, 
                df=session.buildings.df, stroke=0,
            )
            
            # stroke according to connection status:
            session._gis.draw_buildings_connections(
                df=session.buildings.df,
            )            


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

        for popup in [p for p in list(session.popup_menus.values()) if p]:
            popup.draw()

        for tangible in [t for t in list(session.tangibles.values()) if t]:
            if tangible.id in session.popup_menus.keys() and session.popup_menus[tangible.id] is not None and tangible.id not in session.buildings.df['tangible'].unique(): continue
            pygame.draw.circle(
                surface=tangible.surface,
                color=pygame.Color(
                    session.user_colors[tangible.id % session.num_of_users][0],
                    session.user_colors[tangible.id % session.num_of_users][1],
                    session.user_colors[tangible.id % session.num_of_users][2],
                    session.global_alpha),
                center=tangible.surface.get_rect().center,
                radius=115
            )
            pos = tangible.surface.get_rect(center = tangible.surface.get_rect(center = tangible.position).center)
            canvas.blit(tangible.surface, pos)
