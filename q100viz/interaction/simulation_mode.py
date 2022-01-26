import numpy as np
import pandas as pd

import q100viz.session as session
import pygame

class SimulationMode:
    def __init__(self):
        '''in collect_data, q100viz will collect incoming data from the ABM and compile it into a list; send_data will flush it to q100_info. The handles shall be received from the ABM'''
        self.state_handles = ['collect_data', 'send_data']
        self.mode = 'collect_data'
        self.simulation_step = 0

        self.previous_tick = -1

        self.simulation_df = pd.DataFrame(columns=['step', 'buildings'])

    def process_event(self, event, config):
        pass

    def update(self):

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
        stats.send_dataframe_as_json(self.simulation_df)
        if session.verbose:
            self.simulation_df.set_index('step').to_csv('simulation_df.csv')
            self.simulation_df.set_index('step').to_json('simulation_df.json', default_handler=str)