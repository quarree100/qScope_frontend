''' The Questionnaire Mode provides questions that are to be answered by the user in order to assess their mindset/positioning towards Renewable Energies and to evaluate their general acceptance of the project. '''

import pygame
import pandas as pd
import json

import q100viz.keystone as keystone
import q100viz.session as session
from q100viz.interaction.interface import ModeSelector
from config import config

class Questionnaire_Mode():
    def __init__(self):
        session.environment['question_number'] = 0

    def activate(self):
        session.show_polygons = False
        session.grid_1.slider.show_text = False
        session.grid_1.slider.show_controls = False
        session.grid_2.slider.show_text = False
        session.grid_2.slider.show_controls = False
        session.grid_1.slider.handle = 'answer'

        for selector in session.grid_1.selectors:
            selector.show = True  # enable selectors for table 1
            selector.callback_function = ModeSelector.get_next_question
        for selector in session.grid_2.selectors:
            selector.show = False  # disable selectors for table 2

        session.active_handler = session.handlers['questionnaire']
        session.environment['mode'] = 'questionnaire'
        session.stats.send_simplified_dataframe_with_environment_variables(session.buildings[session.buildings.selected], session.environment)

    def process_event(self, event):
        if event.type == pygame.locals.MOUSEBUTTONDOWN:
            session.grid_1.mouse_pressed(event.button)
            session.grid_2.mouse_pressed(event.button)
            session.stats.send_simplified_dataframe_with_environment_variables(
                session.buildings[session.buildings.selected],
                session.environment)

            self.process_grid_change()

    def process_grid_change(self):
        # process grid changes
        for y, row in enumerate(session.grid_1.grid):
            for x, cell in enumerate(row):
                if cell.selected:
                    # ModeSelector
                    for selector in session.grid_1.selectors:
                        if x == selector.x and y == selector.y:
                            selector.callback_function()

    def draw(self, canvas):

        # green slider field:
        points = [[25, 120], [25, 100], [50, 100], [50, 120]]
        points_transformed = session.grid_2.slider.surface.transform(points)
        pygame.draw.polygon(session.grid_2.slider.surface, pygame.Color(200,20,55), points_transformed)

        # red slider field:
        points = [[0, 120], [0, 100], [25, 100], [25, 120]]
        points_transformed = session.grid_2.slider.surface.transform(points)
        pygame.draw.polygon(session.grid_2.slider.surface, pygame.Color(20,200,55), points_transformed)

    def update(self):
        pass