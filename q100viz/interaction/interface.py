''' Interface Elements needed for User Interaction '''

import pygame
import json
import numpy as np

import q100viz.keystone as keystone
import q100viz.session as session

############################ SLIDER ###################################


class Slider:
    def __init__(self, canvas_size, grid, id, coords, x_cell_range):
        self.value = 0
        self.previous_value = 0
        self.group = -1
        self.id = id  # unique identifier for slider
        self.show_text = True  # display slider control text on grid
        self.show_controls = True
        # {slider : (x_min, x_max)}  # which cells to react to
        self.x_cell_range = x_cell_range

        self.color = pygame.Color(125, 125, 125)  # slider area

        self.handle = None
        self.previous_handle = None
        self.last_change = session.seconds_elapsed  # time of last slider change

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
                              'environmental_engagement', 'game_stage', 'num_connections', 'scenario_energy_prices', 'default']

        self.human_readable_value = {None: ''}
        for key in self.VALID_HANDLES:
            self.human_readable_value[key] = ''
        self.human_readable_function = {
            'connection_to_heat_grid': "Wärmenetzanschluss",
            'refurbished': "Sanierung",
            'environmental_engagement': "Energiebewusstsein",
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

                    if self.show_controls:
                        pygame.draw.polygon(
                            self.surface, cell.color, rect_points, stroke)

                # slider control texts:
                if self.show_text and cell.y == len(self.grid.grid) - 1:
                    font = pygame.font.SysFont('Arial', 10)
                    self.surface.blit(
                        font.render(str(cell.handle)[
                                    :8], True, (255, 255, 255)),
                        [rect_points[0][0], rect_points[0][1] + 30]
                    )

        font = pygame.font.SysFont('Arial', 18)

        if self.show_text:
            # display human readable slider name:
            self.surface.blit(font.render(str(self.human_readable_function[self.handle]), True, (255, 255, 255)), [
                              self.coords_transformed[0][0], self.coords_transformed[0][1] - 20])

            # display slider value:
            self.surface.blit(font.render(str(self.human_readable_value[self.handle]), True, (
                255, 255, 255)), (self.coords_transformed[3][0] - 100, self.coords_transformed[3][1]-20))

        canvas.blit(self.surface, (0, 0))

    def draw_area(self):
        pygame.draw.polygon(self.surface, self.color, self.coords_transformed)

        # draw vertical middle line for some handles:
        if self.handle in ['refurbished']:
            pygame.draw.line(self.surface, pygame.Color(255, 255, 255), (self.coords_transformed[0][0] + (self.coords_transformed[3][0] - self.coords_transformed[0][0]) / 2, self.coords_transformed[0][1] + 2),
                             (self.coords_transformed[0][0] + (self.coords_transformed[3][0] - self.coords_transformed[0][0]) / 2, self.coords_transformed[1][1] + 2), width=2)

        if self.handle == 'connection_to_heat_grid':
            pygame.draw.line(self.surface, pygame.Color(255, 255, 255), (self.coords_transformed[0][0] + (self.coords_transformed[3][0] - self.coords_transformed[0][0]) * 0.2, self.coords_transformed[0][1] + 2),
                             (self.coords_transformed[0][0] + (self.coords_transformed[3][0] - self.coords_transformed[0][0]) * 0.2, self.coords_transformed[1][1] + 2), width=2)

    def transform(self):
        self.coords_transformed = self.surface.transform(self.coords)

    def update(self):
        ''' TODO: set up a struct (maybe csv) to import standard values >> this section should be automatized!
        e.g.
        if self.handle == 'name':
            session.environment['name'] = val_from_struct * slider_val
        '''
        if self.value is not self.previous_value:
            # globals:
            if self.handle == 'game_stage':
                handler = [key for key in ['buildings_interaction', 'simulation',
                                        'individual_data_view', 'total_data_view']][int(self.value * 4)]
                print(handler)
                session.active_handler = session.handlers[handler]
                session.active_handler.activate()  # TODO: add confidence delay!

            elif self.handle == 'num_connections':
                session.environment['scenario_num_connections'] = int(
                    self.value * len(session.buildings.df.index))
                self.human_readable_value['num_connections'] = int(
                    self.value * len(session.buildings.df.index))

                # connect additional buildings as set in scenario:
                if session.environment['scenario_num_connections'] > 0:
                    # reset:
                    if not session.scenario_selected_buildings.empty:
                        session.scenario_selected_buildings['selected'] = False
                        session.scenario_selected_buildings['connection_to_heat_grid'] = False
                        session.buildings.df.update(
                            session.scenario_selected_buildings)

                    # sample data:
                    try:
                        session.scenario_selected_buildings = session.buildings.df.sample(
                            n=session.environment['scenario_num_connections'])
                    except Exception as e:
                        print("max number of possible samples reached. " + str(e))
                        session.log += "\n%s" % e

                    # drop already selected buildings from list:
                    for buildings_group in session.buildings_groups_list:
                        for idx in buildings_group.index:
                            if idx in session.scenario_selected_buildings.index:
                                session.scenario_selected_buildings = session.scenario_selected_buildings.drop(
                                    idx)

                    # select and connect sampled buildings:
                    session.scenario_selected_buildings['selected'] = True
                    session.scenario_selected_buildings['connection_to_heat_grid'] = True
                    session.buildings.df.update(
                        session.scenario_selected_buildings)
                    print("selecting random {0} buildings:".format(
                        session.environment['scenario_num_connections']))

                else:  # value is 0: deselect all
                    session.scenario_selected_buildings['selected'] = False
                    session.scenario_selected_buildings['connection_to_heat_grid'] = False
                    session.buildings.df.update(
                        session.scenario_selected_buildings)

            elif self.handle == 'scenario_energy_prices':
                session.environment['scenario_energy_prices'] = [
                    '2018', '2021', '2022'][int(self.value * 2)]
                self.human_readable_value['scenario_energy_prices'] = [
                    '2018', '2021', '2022'][int(self.value * 2)]

            # household-specific:
            if self.handle == 'connection_to_heat_grid':
                session.buildings.df.loc[((
                    session.buildings.df.selected == True) & (session.buildings.df.group == self.group)), 'connection_to_heat_grid'] = False if self.value <= 0.2 else np.interp((self.value), [0.2, 1], [2020, session.handlers['simulation'].max_year])
                self.human_readable_value['connection_to_heat_grid'] = "n.a." if self.value <= 0.2 else int(
                    np.interp(float(self.value), [0.2, 1], [2020, 2045]))

            elif self.handle == 'refurbished':
                session.buildings.df.loc[(
                    session.buildings.df.selected == True) & (session.buildings.df.group == self.group), 'refurbished'] = self.value > 0.5
                self.human_readable_value['refurbished'] = 'saniert' if self.value > 0.5 else 'unsaniert'

            elif self.handle == 'environmental_engagement':
                session.buildings.df.loc[(
                    session.buildings.df.selected == True) & (session.buildings.df.group == self.group), 'environmental_engagement'] = self.value > 0.5
                self.human_readable_value['environmental_engagement'] = self.value

            # questionnaire:
            elif self.handle == 'answer':
                session.environment['answer'] = 'no' if self.value >= 0.5 else 'yes'

            elif self.handle == 'next_question':
                if session.seconds_elapsed > self.last_change + 1:  # some delay for stable interaction
                    if self.toggle_question:
                        if self.value >= 0.5:
                            self.toggle_question = not self.toggle_question
                            if session.active_handler is session.handlers['questionnaire']:
                                session.active_handler.get_next_question()
                            self.last_change = session.seconds_elapsed
                    else:
                        if self.value < 0.5:
                            self.toggle_question = not self.toggle_question
                            if session.active_handler is session.handlers['questionnaire']:
                                session.active_handler.get_next_question()
                            self.last_change = session.seconds_elapsed

            session.api.send_message(json.dumps(session.environment))
            session.api.send_message(json.dumps(
                session.buildings.make_buildings_groups_dict()))

            self.previous_value = self.value

    def update_handle(self, cell_handle, cell_id):
        if self.show_controls:
            self.handle = cell_handle
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
