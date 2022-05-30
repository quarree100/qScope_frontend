''' The Questionnaire Mode provides questions that are to be answered by the user in order to assess their mindset/positioning towards Renewable Energies and to evaluate their general acceptance of the project. '''

import pygame
import pandas as pd
import json
import numpy

import q100viz.keystone as keystone
import q100viz.session as session
from config import config

class DataView_Mode():
    def __init__(self):
        self.name = 'data_view'

    def activate(self):
        session.active_handler = self
        session.environment['mode'] = self.name

        session.show_polygons = False
        session.show_basemap = False

        # setup sliders:
        session.grid_1.slider.show_text = False
        session.grid_1.slider.show_controls = False
        session.grid_2.slider.show_text = False
        session.grid_2.slider.show_controls = False
        # session.grid_1.slider.handle = 'answer'
        # session.grid_2.slider.handle = 'next_question'

        session.stats.send_dataframe_with_environment_variables(None, session.environment)

    def process_event(self, event):
        if event.type == pygame.locals.MOUSEBUTTONDOWN:
            session.grid_1.mouse_pressed(event.button)
            session.grid_2.mouse_pressed(event.button)
            session.stats.send_simplified_dataframe_with_environment_variables(
                session.buildings[session.buildings.selected],
                session.environment)

            self.process_grid_change()

            # session.stats.send_dataframe_using_keys(session.buildings[session.buildings['connection_to_heat_grid'] == True], keys=["address","connection_to_heat_grid"])

            connected_buildings = pd.DataFrame(data=[
                {'connected_buildings' : len(session.buildings[session.buildings['connection_to_heat_grid'] == True])}])
            session.stats.send_dataframe_as_json(connected_buildings)

    def process_grid_change(self):
        pass

    def draw(self, canvas):

        pass

    def update(self):
        pass