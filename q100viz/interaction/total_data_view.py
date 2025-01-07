''' The Questionnaire Mode provides questions that are to be answered by the user in order to assess their mindset/positioning towards Renewable Energies and to evaluate their general acceptance of the project. '''

import pygame
import pandas as pd
import datetime

import q100viz.session as session
from q100viz.devtools import devtools as devtools

class DataViewTotal_Mode():
    def __init__(self):
        self.name = 'total_data_view'
        self.mode_token_selection_time = datetime.datetime.now()
        self.activation_buffer_time = 2  # seconds before simulation begins

    def activate(self):
        '''do not call! This function is automatically called in main loop. Instead, enable a mode by setting session.active_mode = session.[mode]'''

        session.environment['mode'] = self.name

        session.show_polygons = True
        session.show_basemap = True

        session.api.send_dict(session.environment)

    def process_event(self, pos):
        connected_buildings = pd.DataFrame(data=[
            {'connected_buildings' : len(session.buildings.df[session.buildings.df['connection_to_heat_grid'] >= 0])}])
        session.api.send_dataframe_as_json(connected_buildings)
        
    def process_tangible_event(self, tangible_id, pos, rotation):
        pass        

    def draw(self, canvas):
        # draw GIS layers:
        if session.show_polygons:
            session._gis.draw_linestring_layer(
                canvas, session._gis.nahwaermenetz, (217, 9, 9), 3)
            session._gis.draw_buildings_connections(
                session.buildings.df)  # draw lines to closest heat grid

            session._gis.draw_polygon_layer(
                surface=canvas, 
                df=session.buildings.df[(session.buildings.df['connection_to_heat_grid'] >= 0) | (session.buildings.df['group'] >= 0)],
                stroke=0
                )