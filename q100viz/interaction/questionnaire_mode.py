''' The Questionnaire Mode provides questions that are to be answered by the user in order to assess their mindset/positioning towards Renewable Energies and to evaluate their general acceptance of the project. '''

import pygame
import pandas as pd

import q100viz.keystone as keystone
import q100viz.session as session
import q100viz.stats as stats
from q100viz.interaction.generic_mode import Generic_Mode
from config import config

class Questionnaire_Mode():
    def __init__(self):
        pass

    def activate(self):
        session.show_polygons = False
        session.grid_1.slider.show_text = False  # without text
        session.grid_1.slider.handle = 'yes_no'
        session.grid_2.slider.show_text = False

        for grid in session.grid_1, session.grid_2:
            for selector in grid.selectors:
                selector.show = False  # disable selectors (InputMode will be started automatically when all questions are answered)

        session.active_handler = session.handlers['questionnaire']
        session.environment['mode'] = 'questionnaire'

    def process_event(self, event, config):
        if event.type == pygame.locals.MOUSEBUTTONDOWN:
            session.grid_1.mouse_pressed(event.button)
            session.grid_2.mouse_pressed(event.button)
            session.stats.send_simplified_dataframe_with_environment_variables(
                session.buildings[session.buildings.selected],
                session.environment)

    def draw(self, canvas):

        # green slider field:
        points = [[0, 120], [0, 100], [25, 100], [25, 120]]
        points_transformed = session.grid_2.slider.surface.transform(points)
        pygame.draw.polygon(session.grid_2.slider.surface, pygame.Color(200,20,55), points_transformed)

        # red slider field:
        points = [[25, 120], [25, 100], [50, 100], [50, 120]]
        points_transformed = session.grid_2.slider.surface.transform(points)
        pygame.draw.polygon(session.grid_2.slider.surface, pygame.Color(20,200,55), points_transformed)



    def update(self):
        pass