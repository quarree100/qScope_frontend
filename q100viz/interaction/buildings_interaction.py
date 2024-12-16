''' Input Households Mode: Interact with building-specific parameters using the map '''

import json
import shapely
import pygame
import datetime

import q100viz.session as session
from q100viz.devtools import devtools
from q100viz.settings.config import config
from q100viz.interaction.PopupMenu import TouchMenu, TangibleMenu


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

    def process_event(self, event_pos):

        buildings = session.buildings.df

        for popup in [p for p in buildings['popup'] if p]:
            if popup.handle_mouse_button(event_pos): return
                    
    def process_tangible_event(self, tangible_id, pos, rotation):
        buildings = session.buildings.df
        
        # check collision with popups:
        for popup in list(buildings['popup'].values):
            if popup is None: continue
            if popup.radius is not popup.target_radius: return  # animation not complete
            for rect in [i.rect for i in popup.icons.values()]:
                if rect.collidepoint(pos):  # TODO: rect could be defined more precisely as the circle, that it is.
                    print(f"ID {tangible_id} inside popup of building {session.buildings.df.loc[popup.idx, 'address']}: {pos} ∈ {rect.center}")
                    popup.handle_mouse_button(pos)
                    popup.secondary_tangible = tangible_id
                    # close popup if exists:
                    if tangible_id in list(buildings['tangible'].values):
                        bd = buildings[buildings['tangible'] == tangible_id]
                        session.buildings.deselect(bd.index[0])
                    return

        # check collision with buildings:
        if tangible_id in list(buildings['tangible'].values):
            # leave building:
            bd = buildings[buildings['tangible'] == tangible_id]
            if not shapely.Point(pos).within(shapely.geometry.Polygon(bd.loc[bd.index[0], 'polygon'])):
                session.buildings.deselect(bd.index[0])
                return
            else:
                return
        
        # building selected:
        for idx in buildings.index:
            if shapely.Point(pos).within(shapely.geometry.Polygon(buildings.loc[idx, 'polygon'])):
                buildings.at[idx, 'tangible'] = tangible_id

                buildings.at[idx, 'selected'] = True
                buildings.at[idx, 'group'] = tangible_id % 4
                TangibleMenu(
                    session.viewport,
                    pos,
                    displace=(0, 200),
                    idx=idx,
                    start_rotation=rotation
                )
                buildings.loc[idx, 'popup'].primary_tangible = tangible_id
                
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

        for popup in list(session.popup_menus.values()):
            popup.draw()
