''' Interface Elements needed for User Interaction '''

import pygame
import json
import random

import q100viz.keystone as keystone
import q100viz.session as session

from config import config

############################ SLIDER ###################################
class Slider:
    def __init__(self, canvas_size, grid, coords):
        self.value = 0
        self.previous_value = 0
        self.show_text = True  # display slider control text on grid
        self.show_controls = True

        self.color = pygame.Color(125, 125, 125)  # slider area

        self.handle = None
        self.previous_handle = None
        self.last_change = session.seconds_elapsed  # time of last slider change

        self.toggle_question = False  # this is used for the activation of the next question in questionnaire mode  # TODO: get slider position initially and set toggle accordingly (Slider should not "start at" this position)

        self.grid = grid  # the slider needs a grid to be able to refer back to it

        # create rectangle around centerpoint:
        self.coords = coords
        self.surface = keystone.Surface(canvas_size, pygame.SRCALPHA)
        self.surface.src_points = [
            [0, 0], [0, 100], [100, 100], [100, 0]]

        self.surface.dst_points = grid.surface.dst_points  # relative coordinate system

        self.surface.calculate(session.viewport.transform_mat)  # get matrix to transform by

        self.coords_transformed = self.surface.transform(coords)

    def render(self, canvas=None):
        canvas.blit(self.surface, (0,0))

        # print function text on sliderControl cells:
        for cell, rect_points in self.grid.rects_transformed:
            if cell.handle is not None and self.show_controls:  # cells have handles if set in csv
                stroke = 4 if cell.selected else 1

                if cell.selected:
                    self.color = cell.color

                if session.show_polygons: pygame.draw.polygon(self.grid.surface, cell.color, rect_points, stroke)

    def draw_area(self):
        pygame.draw.polygon(self.surface, self.color, self.coords_transformed)

    def transform(self):
        self.coords_transformed = self.surface.transform(self.coords)

    def update(self):
        ''' TODO: set up a struct (maybe csv) to import standard values >> this section should be automatized!
        e.g.
        if self.handle == 'name':
            session.environment['name'] = val_from_struct * slider_val
        '''

        # globals:
        if self.handle == 'year':
            session.environment['year'] = 2020 + \
                int(self.value * 30) # ranges from 2020 to 2050
        elif self.handle == 'renovation_cost':
            session.environment['renovation_cost'] = int(
                self.value * 10000)  # ranges from 0 to 10,000€
        elif self.handle == 'CO2-prize':
            session.environment['CO2-prize'] = 55 + \
                self.value * 195  # ranges from 55 to 240€/t
        elif self.handle == 'connection_speed':
            session.environment['connection_speed'] = self.value

        # household-specific:
        elif self.handle == 'CO2-emissions':
            session.buildings.loc[(
                session.buildings.selected == True), 'CO2'] = self.value  # sets CO2-value of selected buildings to slider value (absolute)
        elif self.handle == 'electricity_supplier':
            if self.value >= 0 and self.value < 0.33:
                session.buildings.loc[(session.buildings.selected == True), 'electricity_supplier'] = 'gray'
            elif self.value >= 0.33 and self.value < 0.66:
                session.buildings.loc[(session.buildings.selected == True), 'electricity_supplier'] = 'mix'
            if self.value >= 0.66 and self.value < 1:
                session.buildings.loc[(session.buildings.selected == True), 'electricity_supplier'] = 'green'
        # elif self.handle == 'investment':
        #     # ranges from 0 to 10,000€
        #     session.environment['investment'] = self.value * 10000
        elif self.handle == 'connection_to_heat_grid':
            session.buildings.loc[(
                session.buildings.selected == True), 'connection_to_heat_grid'] = self.value > 0.5
        elif self.handle == 'refurbished':
            session.buildings.loc[(
                session.buildings.selected == True), 'refurbished'] = self.value > 0.5

        # questionnaire:
        elif self.handle == 'answer':
            session.environment['answer'] = 'no' if self.value >= 0.5 else 'yes'

        elif self.handle == 'next_question':
            if session.seconds_elapsed > self.last_change + 1:  # some delay for stable interaction
                if self.toggle_question:
                    if self.value >= 0.5:
                        self.toggle_question = not self.toggle_question
                        if session.active_handler is session.handlers['questionnaire']: session.active_handler.get_next_question()
                        self.last_change = session.seconds_elapsed
                else:
                    if self.value < 0.5:
                        self.toggle_question = not self.toggle_question
                        if session.active_handler is session.handlers['questionnaire']: session.active_handler.get_next_question()
                        self.last_change = session.seconds_elapsed

        if self.previous_value is not self.value:
            # TODO: this is a workaround! the upper functions enables questionnaire communication, the latter one does not refresh the buildings status in infoscreen constantly.. --> create better functions in stats!
            if session.active_handler == session.handlers['questionnaire']:
                session.stats.send_message(json.dumps(session.environment))
            else:
                session.stats.send_simplified_dataframe_with_environment_variables(session.buildings[session.buildings.selected], session.environment)
            self.previous_value = self.value

############################### MODE SELECTOR #########################
class ModeSelector:
    def __init__(self, grid, x, y, color, callback_function):
        self.show = True
        self.name = "NAME"
        self.color = pygame.Color(color)
        self.grid = grid
        self.x = x
        self.y = y
        self.callback_function = callback_function

    def render(self):

        if self.show:
            for cell, rect_points in self.grid.rects_transformed:
                # ModeSelector
                if cell.x == self.x and cell.y == self.y:
                    stroke = 4 if cell.selected else 1
                    pygame.draw.polygon(self.grid.surface, self.color, rect_points, stroke)
                    font = pygame.font.SysFont('Arial', 8)

                    # display mode name
                    self.grid.surface.blit(
                        font.render(self.name,
                            True, (255, 255, 255)),
                            [rect_points[0][0] + 10, rect_points[0][1]+ 35]
                    )

    def callback_activate_input_mode():
        print("activating input mode B")
        session.handlers['input_households'].activate()

    def callback_activate_input_environment():
        print("activating input mode A")
        session.handlers['input_environment'].activate()

    def callback_activate_simulation_mode():
        print("activating simulation mode")
        session.handlers['simulation'].activate()

    def callback_get_next_question():
        session.handlers['questionnaire'].get_next_question()

    def callback_none():
        pass

class MousePosition:
    def __init__(self, canvas_size):
        self.surface = keystone.Surface(canvas_size, pygame.SRCALPHA)


    def draw(self, surface, x, y):
        pygame.draw.circle(surface, pygame.color.Color(50, 160, 123), (x, y), 20)