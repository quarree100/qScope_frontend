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
                (session.buildings.selected == True), 'EEH'] *= session.buildings.loc[
                    (session.buildings.selected == True), 'EEH']
            session.buildings['EEH'] += np.random.uniform(-0.5, 0.5)

            self.simulation_df.loc[len(self.simulation_df.index)] = [self.simulation_step, session.buildings[session.buildings.selected == True]]

            self.simulation_step += 1
            self.previous_tick = session.seconds_elapsed

    def draw(self, canvas):
        pass

    def send_data(self, stats):
        stats.send_dataframe_as_json(self.simulation_df)