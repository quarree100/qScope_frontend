''' Simulation Mode fakes parameter changes for buildings later done by the ABM'''

import numpy as np
import pandas as pd
import json

import q100viz.session as session
import pygame


class SimulationMode:
    def __init__(self):
        self.simulation_step = 0

        self.previous_tick = -1  # stores moment of last step change

        self.simulation_df = pd.DataFrame(columns=['step', 'buildings'])

    def process_event(self, event, config):
        if event.type == pygame.locals.MOUSEBUTTONDOWN:
            session.grid_1.mouse_pressed(event.button)
            session.grid_2.mouse_pressed(event.button)
            session.flag_export_canvas = True

    def update(self):

        # process grid changes
        for grid in [session.grid_1, session.grid_2]:
            for y, row in enumerate(grid.grid):
                for x, cell in enumerate(row):
                    if cell.selected and y == len(grid.grid)-1:
                        # enter input mode:
                        if x == int(session.grid_settings['ncols'] * 2 / 3):
                            if session.active_handler == session.handlers['simulation']:
                                self.send_data(session.stats)
                            session.active_handler = session.handlers['tui']
                            grid.deselect(int(session.grid_settings['ncols'] * 2 / 3 + 2), len(grid.grid) - 1)
                            print(session.active_handler)

        ######################## SIMULATION UPDATE ####################
        # one step per second:
        if session.seconds_elapsed != self.previous_tick:

            # mockup data:
            session.buildings.loc[
                (session.buildings.selected == True), 'CO2'] *= session.buildings.loc[
                    (session.buildings.selected == True), 'CO2']
            session.buildings['CO2'] += np.random.uniform(-0.5, 0.5)

            if not session.buildings[session.buildings.selected == True].empty:
                self.simulation_df.loc[len(self.simulation_df.index)] = [self.simulation_step, session.buildings[session.buildings.selected == True]]

            self.simulation_step += 1
            self.previous_tick = session.seconds_elapsed

    def draw(self, canvas):
        if session.verbose:
            font = pygame.font.SysFont('Arial', 20)
            canvas.blit(font.render(str(self.simulation_step), True, (255,255,255)), (300,900))

        if len(session.buildings[session.buildings.selected]):
            # highlight selected buildings
            session.gis.draw_polygon_layer(
                canvas,
                session.buildings[session.buildings.selected], 2, (255, 0, 127)
            )

    def send_data(self, stats):
        stats.send_dataframe_as_json(pd.DataFrame(self.simulation_df))

        # save as csv in global data folder:
        self.simulation_df.set_index('step').to_csv('../data/simulation_df.csv')
        # self.simulation_df.to_json('../data/simulation_df.json')
