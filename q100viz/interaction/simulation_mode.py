''' Simulation Mode fakes parameter changes for buildings later done by the ABM'''

import numpy as np
import pandas
import json
import pygame

import q100viz.session as session
from q100viz.simulation import Simulation
class SimulationMode:
    def __init__(self):
        self.name = 'simulation'

    def activate(self):
        session.environment['mode'] = self.name
        session.active_handler = self

        # display setup:
        for slider in session.grid_1.slider, session.grid_2.slider:
            slider.show_text = False
            slider.show_controls = False

        # provide data:
        outputs = pandas.DataFrame(columns=['id', 'name', 'framerate'])
        outputs.loc[len(outputs)] = ['0', 'neighborhood', '1']
        outputs.loc[len(outputs)] = ['1', 'households_income_bar', '5']

        params = pandas.DataFrame(columns=['name', 'type', 'value', 'var'])
        params.loc[len(params)] = ['Alpha scenario', 'STRING', 'Static_mean', 'alpha_scenario']
        params.loc[len(params)] = ['Carbon price scenario', 'STRING', 'A-Conservative', 'carbon_price_scenario']
        params.loc[len(params)] = ['Energy prices scenario', 'STRING', 'Prices_Project start', 'energy_price_scenario']
        params.loc[len(params)] = ['Q100 OpEx prices scenario', 'STRING', '12 ct / kWh (static)', 'q100_price_opex_scenario']
        params.loc[len(params)] = ['Q100 CapEx prices scenario', 'STRING', '1 payment', 'q100_price_capex_scenario']
        params.loc[len(params)] = ['Q100 Emissions scenario', 'STRING', 'Constant_50g / kWh', 'q100_emissions_scenario']
        # params.loc[len(params)] = ['keep_seed', 'bool', 'true']

        simulation = Simulation()

        simulation.make_xml(params, outputs, experiment_name='agent_decision_making', finalStep=1000)
        simulation.run_script('/opt/gama-platform/headless/gama-generated-headless.xml')

        # send data
        session.stats.send_dataframe_with_environment_variables(None, session.environment)

    def process_event(self, event):
        if event.type == pygame.locals.MOUSEBUTTONDOWN:
            session.grid_1.mouse_pressed(event.button)
            session.grid_2.mouse_pressed(event.button)
            session.flag_export_canvas = True

            self.process_grid_change()

    def process_grid_change(self):
        for grid in [session.grid_1, session.grid_2]:
            for y, row in enumerate(grid.grid):
                for x, cell in enumerate(row):
                    if cell.selected:
                        pass

        session.stats.send_simplified_dataframe_with_environment_variables(session.buildings[session.buildings.selected], session.environment)

    def update(self):

        pass

    def draw(self, canvas):
        if session.verbose:
            font = pygame.font.SysFont('Arial', 40)
            canvas.blit(font.render("Simulation running...", True, (255,255,255)), (session.canvas_size[0]/2, session.canvas_size[1]/2))

        if len(session.buildings[session.buildings.selected]):
            # highlight selected buildings
            session.gis.draw_polygon_layer(
                canvas,
                session.buildings[session.buildings.selected], 2, (255, 0, 127)
            )

    def send_data(self, stats):
        stats.send_dataframe_as_json(pandas.DataFrame(self.simulation_df))

        # save as csv in global data folder:
        # self.simulation_df.set_index('step').to_csv('../data/simulation_df.csv')
        # self.simulation_df.to_json('../data/simulation_df.json')
