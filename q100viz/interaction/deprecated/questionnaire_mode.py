''' The Questionnaire Mode provides questions that are to be answered by the user in order to assess their mindset/positioning towards Renewable Energies and to evaluate their general acceptance of the project. '''

import pygame
import pandas as pd
import json
import numpy

import q100viz.keystone as keystone
import q100viz.session as session
from q100viz.settings.config import config

class Questionnaire_Mode():
    def __init__(self):
        self.name = 'questionnaire'
        self.question_index = 0
        self.answer = 'no'
        # session.question = session.questions[self.question_index]

    def activate(self):
        session.environment['mode'] = self.name

        session.show_polygons = False
        session.show_basemap = False

        # setup sliders:
        session.grid_1.sliders['slider0'].show_text = True
        session.grid_1.sliders['slider0'].show_controls = True

        session.grid_1.sliders['slider1'].handle = 'answer'
        session.grid_1.sliders['slider1'].show_text = False
        session.grid_1.sliders['slider1'].show_controls = False

        session.grid_2.sliders['slider2'].show_text = False
        session.grid_2.sliders['slider2'].show_controls = False
        session.grid_2.sliders['slider2'].handle = 'next_question'

        session.active_mode = session.questionnaire
        session.environment['mode'] = self.name

        session.api.send_df_with_session_env(None)

    def process_event(self, event):
        if event.type == pygame.locals.MOUSEBUTTONDOWN:
            session.grid_1.mouse_pressed(event.button)
            session.grid_2.mouse_pressed(event.button)
            session.api.send_simplified_dataframe_with_environment_variables(
                session.buildings.df[session.buildings.df.selected],
                session.environment)

            self.process_grid_change()

    def process_grid_change(self):
        # interactions only caused by sliders in this mode.
        pass

    def draw(self, canvas):

        # left slider green field:
        points = [[75, 120], [75, 100], [100, 100], [100, 120]]
        points_transformed = session.grid_1.sliders['slider0'].surface.transform(points)
        pygame.draw.polygon(session.grid_1.sliders['slider0'].surface, pygame.Color(200,20,55), points_transformed)

        # left slider red field:
        points = [[50, 120], [50, 100], [75, 100], [75, 120]]
        points_transformed = session.grid_1.sliders['slider0'].surface.transform(points)
        pygame.draw.polygon(session.grid_1.sliders['slider0'].surface, pygame.Color(20,200,55), points_transformed)

        # right slider:
        points = [[25, 120], [25, 100], [50, 100], [50, 120]] if session.grid_2.sliders['slider2'].toggle_question else [[0, 120], [0, 100], [25, 100], [25, 120]]
        points_transformed = session.grid_2.sliders['slider2'].surface.transform(points)
        a = 100 + abs(int(numpy.sin(pygame.time.get_ticks() / 1000) * 105))
        pygame.draw.polygon(session.grid_2.sliders['slider2'].surface, pygame.Color(230, 249, 255, a), points_transformed)


    def get_next_question(self):
        print("getting next question")
        # self.question_index = (self.question_index + 1 ) % len(session.questions)
        self.question_index += 1

        # get next question
        if self.question_index is not session.num_of_questions:
            # session.question = session.questions[self.question_index]
            session.api.send_dataframe_as_json(
                pd.DataFrame(data={"question_number" : [self.question_index]}))
        else:  # leave questionnaire mode, enter input mode
            self.question_index = 0
            session.active_mode = session.input_scenarios


    def update(self):
        pass