''' Interface Elements needed for User Interaction '''

import pygame
import json
import numpy as np

import q100viz.keystone as keystone
import q100viz.session as session
from q100viz.settings.config import config_slider

############################ SLIDER ###################################


class Slider:
    def __init__(self, canvas_size, grid, id, coords, x_cell_range):
        self.value = 0
        self.previous_value = 0
        self.group = -1
        self.id = id  # unique identifier for slider
        self.show_text = True  # display slider control text on grid
        self.show_controls = True
        self.x_cell_range = x_cell_range  # limits of slider handles
        self.physical_slider_area_length = config_slider[id]['PHYSICAL_SLIDER_AREA_LENGTH']  # cm
        self.physical_diff_L = config_slider[id]['PHYSICAL_DIFF_L']  # diff from left side of area to cspy slider detection, in cm
        self.physical_diff_R = config_slider[id]['PHYSICAL_DIFF_R']  # diff to right side of area to cspy slider detection, in cm

        self.color = pygame.Color(125, 125, 125)  # slider area

        self.handle = None
        self.previous_handle = None
        self.last_change = session.seconds_elapsed  # time of last slider change

        self.min_connection_year = 2020
        self.max_connection_year = 2040
        self.min_refurb_year = 2020
        self.max_refurb_year = 2040

        # this is used for the activation of the next question in questionnaire mode  # TODO: get slider position initially and set toggle accordingly (Slider should not "start at" this position)
        self.toggle_question = False

        self.grid = grid  # the slider needs a grid to be able to refer back to it

        # create rectangle around centerpoint:
        self.coords = coords
        self.surface = keystone.Surface(canvas_size, pygame.SRCALPHA)
        self.surface.src_points = [
            [0, 0], [0, 100], [100, 100], [100, 0]]

        self.surface.dst_points = grid.surface.dst_points  # relative coordinate system

        # get matrix to transform by
        self.surface.calculate(session.viewport.transform_mat)

        # stores coordinates as [[bottom-left.x, bottom-left.y], [top-left.x, top-left.y] [top-right.x, top-right.y], [bottom-right.x, bottom-right.y]]
        self.coords_transformed = self.surface.transform(coords)
        self.VALID_HANDLES = ['connection_to_heat_grid', 'refurbished',
                              'save_energy', 'game_stage', 'num_connections', 'scenario_energy_prices', 'default']

        self.human_readable_value = {None: ''}
        for key in self.VALID_HANDLES:
            self.human_readable_value[key] = ''
        self.human_readable_function = {
            'connection_to_heat_grid': "Wärmenetzanschluss",
            'refurbished': "Sanierung",
            'save_energy': "Energie sparen",
            'game_stage': "Spielmodus",
            'num_connections': "zusätzliche Anschlüsse",
            'scenario_energy_prices': "Energiekostenszenario",
            None: "Slider-Funktion auswählen"
        }

    def render(self, canvas=None):
        # slider controls → set slider color
        # alpha value for unselected cells
        a = 100 + abs(int(np.sin(pygame.time.get_ticks() / 1000) * 105))

        self.color = pygame.Color(0, 0, 0, 0)
        for cell, rect_points in self.grid.rects_transformed:
            # cells have handles if set in csv
            if cell.handle is not None and cell.x in range(self.x_cell_range[0], self.x_cell_range[1]):
                if self.show_controls:
                    stroke = 4 if cell.selected else 0

                    if cell.selected:
                        if cell.handle not in session.mode_selector_handles:  # do not adopt color of mode selectors
                            cell.color = pygame.Color(
                                cell.color.r, cell.color.g, cell.color.b, 255)
                            self.color = cell.color
                    else:
                        cell.color = pygame.Color(
                            cell.color.r, cell.color.g, cell.color.b, a)

                    # draw slider handles:
                    if self.show_controls:
                        pygame.draw.polygon(
                            self.surface, cell.color, rect_points, stroke)

                # slider control texts:
                if self.show_text and cell.y == len(self.grid.grid) - 1:
                    font = pygame.font.SysFont('Arial', 10)
                    handle_string = ""
                    if cell.handle == "connection_to_heat_grid":
                        handle_string = "Anschluss"
                    elif cell.handle == "refurbished":
                        handle_string = "Sanierung"
                    elif cell.handle == "save_energy":
                        handle_string = "Energiesparen"
                    if cell.handle == "scenario_energy_prices":
                        handle_string = "Energiepreise"
                    if cell.handle == "num_connections":
                        handle_string = "Anschlüsse"
                    self.surface.blit(
                        font.render(handle_string, True, (255, 255, 255)),
                        [rect_points[0][0], rect_points[0][1] + 35]
                    )

        font = pygame.font.SysFont('Arial', 18)

        if self.show_text:
            # display human readable slider name:
            self.surface.blit(font.render(str(self.human_readable_function[self.handle]), True, (255, 255, 255)), [
                              self.coords_transformed[0][0], self.coords_transformed[0][1] - 20])

            # display human readable slider value:
            self.surface.blit(font.render(str(self.human_readable_value[self.handle]), True, (
                255, 255, 255)), (self.coords_transformed[3][0] - 100, self.coords_transformed[3][1]-20))

        if session.VERBOSE_MODE:
            self.surface.blit(font.render(str(self.value), True, (
                255, 255, 255)), (self.coords_transformed[3][0] - 20, self.coords_transformed[3][1]-20))

        canvas.blit(self.surface, (0, 0))

    def draw_area(self):

        if self.handle == 'save_energy':
            pygame.draw.line(
                self.surface, pygame.Color(255, 255, 255), (self.coords_transformed[0][0] + (self.coords_transformed[3][0] - self.coords_transformed[0][0]) / 2, self.coords_transformed[0][1] + 2),
                (self.coords_transformed[0][0] + (self.coords_transformed[3][0] - self.coords_transformed[0][0]) / 2, self.coords_transformed[1][1] + 2), width=2)

            # red field:
            c = self.coords
            points = [
                c[0],  # bottom left
                c[1],  # top left
                [c[2][0] - c[1][0]/2, c[2][1]],  # top right
                [c[3][0] - c[1][0]/2, c[3][1]]]  # bottom right
            points_transformed = self.surface.transform(points)
            pygame.draw.polygon(self.surface, pygame.Color(130,20,55), points_transformed)

            # green field:
            c = self.coords
            points = [
                [c[0][0] + (c[3][0] - c[0][0]) / 2, c[0][1]],  # bottom left
                [c[1][0] + (c[2][0] - c[1][0]) / 2, c[1][1]],  # top left
                c[2],  # top right
                c[3]]  # bottom right
            points_transformed = self.surface.transform(points)
            pygame.draw.polygon(self.surface, pygame.Color(20,130,55), points_transformed)

        if self.handle in ['connection_to_heat_grid', 'refurbished']:
            min_year = self.min_connection_year if self.handle is 'connection_to_heat_grid' else self.min_refurb_year
            max_year = self.max_connection_year if self.handle is 'connection_to_heat_grid' else self.max_refurb_year


            x0 = self.coords_transformed[0][0]  # in px
            x3 = self.coords_transformed[3][0]  # in px
            y0 = self.coords_transformed[0][1]  # in px
            y1 = self.coords_transformed[1][1]  # in px
            y3 = self.coords_transformed[3][1]  # in px

            # physical slider area dimensions:
            s0 = x0 + (x3 - x0) * self.physical_diff_L/self.physical_slider_area_length  # in px
            s1 = x0 + (x3 - x0) * self.physical_diff_R/self.physical_slider_area_length  # in px

            # red field: no connection
            points = [
                (x0, y0),  # bottom left
                (x0, y1),  # top left
                (s0 + (s1 - s0) * 0.21, y1),  # top right
                (s0 + (s1 - s0) * 0.21, y0)  # bottom right
            ]
            pygame.draw.polygon(self.surface, pygame.Color(130,20,55), points)

            font = pygame.font.SysFont('Arial', 10)

            # intermediate seperators:
            for x in [0.2, 0.6, 1.0]:
                pygame.draw.line(
                    self.surface, pygame.Color(200, 200, 200),
                    (s0 + (s1 - s0) * x, y0 - 35),
                    (s0 + (s1 - s0) * x, y1 + 13), width=1
                    )
                self.surface.blit(font.render(str(int(np.interp((x), [0.2, 1], [min_year, max_year]))), True, (
                    200, 200, 200)), ((s0 + (s1 - s0) * x) - 10, y0 - 35))


            if session.VERBOSE_MODE:
                self.surface.blit(font.render("L", True, (
                    255, 255, 255)), (s0, y3-20))
                self.surface.blit(font.render("|", True, (
                    255, 255, 255)), (s0 + (s1 - s0) * 0.2, y3-20))
                self.surface.blit(font.render("x", True, (
                    255, 255, 255)), ((s0 + (s1 - s0) * self.value) + 5, y3-80))
                self.surface.blit(font.render("R", True, (
                    255, 255, 255)), (s1, y3-20))

    def transform(self):
        self.coords_transformed = self.surface.transform(self.coords)

    def process_value(self):
        ''' TODO: set up a struct (maybe csv) to import standard values >> this section should be automatized!
        e.g.
        if self.handle == 'name':
            session.environment['name'] = val_from_struct * slider_val
        '''
        if self.value is not self.previous_value:

            # household-specific:
            if self.handle == 'connection_to_heat_grid':
                session.buildings.df.loc[((
                    session.buildings.df.selected == True) & (session.buildings.df.group == self.group)), 'connection_to_heat_grid'] = False if self.value <= 0.2 else int(np.interp((self.value), [0.2, 1], [self.min_connection_year, self.max_connection_year]))
                self.human_readable_value['connection_to_heat_grid'] = "n.a." if self.value <= 0.2 else int(
                    np.interp(float(self.value), [0.2, 1], [self.min_connection_year, self.max_connection_year]))

            elif self.handle == 'refurbished':
                session.buildings.df.loc[((
                    session.buildings.df.selected == True) & (session.buildings.df.group == self.group)), 'refurbished'] = False if self.value <= 0.2 else int(np.interp((self.value), [0.2, 1], [self.min_refurb_year, self.max_refurb_year]))
                self.human_readable_value['refurbished'] = "n.a." if self.value <= 0.2 else int(
                    np.interp(float(self.value), [0.2, 1], [self.min_refurb_year, self.max_refurb_year]))

            elif self.handle == 'save_energy':
                session.buildings.df.loc[(
                    session.buildings.df.selected == True) & (session.buildings.df.group == self.group), 'save_energy'] = self.value > 0.5
                self.human_readable_value['save_energy'] = 'ja' if self.value > 0.5 else 'nein'

            # questionnaire:
            elif self.handle == 'answer':
                session.questionnaire.answer = 'no' if self.value >= 0.5 else 'yes'

            elif self.handle == 'next_question':
                if session.seconds_elapsed > self.last_change + 1:  # some delay for stable interaction
                    if self.toggle_question:
                        if self.value >= 0.5:
                            self.toggle_question = not self.toggle_question
                            if session.active_mode is session.questionnaire:
                                session.active_mode.get_next_question()
                            self.last_change = session.seconds_elapsed
                    else:
                        if self.value < 0.5:
                            self.toggle_question = not self.toggle_question
                            if session.active_mode is session.questionnaire:
                                session.active_mode.get_next_question()
                            self.last_change = session.seconds_elapsed

            session.api.send_message(json.dumps(session.environment))
            session.api.send_message(json.dumps(
                session.buildings.get_dict_with_api_wrapper()))

            self.previous_value = self.value

    def update_handle(self, cell_handle, cell_id):
        if self.show_controls:
            self.handle = cell_handle
            self.process_value()  # update values
            self.group = cell_id
            if self.previous_handle is not self.handle:
                session.api.send_message(json.dumps({'sliders': {
                    "id": self.id,
                    "handle": self.handle,
                    "group": self.group}}))
                self.previous_handle = self.handle


class MousePosition:
    def __init__(self, canvas_size):
        self.surface = keystone.Surface(canvas_size, pygame.SRCALPHA)

    def draw(self, surface, x, y):
        pygame.draw.circle(surface, pygame.color.Color(
            50, 160, 123), (x, y), 20)
