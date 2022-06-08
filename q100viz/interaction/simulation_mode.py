''' Simulation Mode fakes parameter changes for buildings later done by the ABM'''

import pandas
import os
import subprocess
import threading
import pygame

import q100viz.session as session
from q100viz.settings.config import config
class SimulationMode:
    def __init__(self):
        self.name = 'simulation'

        self.cwd = os.getcwd()  # hold current working directory to return to later

        self.headless_folder = config['GAMA_HEADLESS_FOLDER']
        self.script = self.headless_folder + 'gama-headless.sh'
        self.model_file = os.path.normpath(os.path.join(self.cwd, config['GAMA_MODEL_FILE']))
        self.output_folder = os.path.normpath(os.path.join(self.cwd, config['GAMA_OUTPUT_FOLDER']))
        self.xml_path = self.headless_folder + '/simulation_parameters.xml'

        print("headless_folder =", self.headless_folder, "\nscript = ", self.script, "\nmodel_file = ", self.model_file, "\noutput_folder = ", self.output_folder)

        self.xml = None

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

        self.make_xml(params, outputs, self.xml_path, 1000, None, 'agent_decision_making')
        self.run_script('/opt/gama-platform/headless/gama-generated-headless.xml')

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

    def make_xml(self, parameters, outputs, xml_output_path, finalStep=None, until=None, experiment_name=None, seed=1.0):
        # header
        xml_temp = ['<Experiment_plan>']
        # if until is not None:
            # xml_temp.append('  <Simulation experiment="{0}" sourcePath="{1}" finalStep="{2}" until="{3}" experiment="{4}" seed="{5}">'.format(str(experiment_name), str(self.model_file), str(finalStep), str(until), str(experiment_name), str(seed)))

        xml_temp.append('  <Simulation experiment="{0}" sourcePath="{1}" finalStep="{2}"'.format(str(experiment_name), str(self.model_file), str(finalStep)))
        if seed is not None: xml_temp.append('seed="{0}"'.format(str(seed)))
        if until is not None: xml_temp.append('until="{0}"'.format(str(until)))
        xml_temp.append('>')

        # else:
        #     xml_temp.append('  <Simulation experiment="{0}" sourcePath="{1}" finalStep="{2}" >'.format(str(experiment_name), str(self.model_file), str(finalStep)))

        # parameters
        xml_temp.append('  <Parameters>')
        for index, row in parameters.iterrows():
            xml_temp.append('    <Parameter name="{0}" type="{1}" value="{2}" var="{3}"/>'.format(row['name'], row['type'], row['value'], row['var']))
        xml_temp.append('  </Parameters>')

        # outputs
        xml_temp.append('  <Outputs>')
        for index, row in outputs.iterrows():
            xml_temp.append('    <Output id="{0}" name="{1}" framerate="{2}" />'.format(row['id'], row['name'], row['framerate']))
        xml_temp.append('  </Outputs>')
        xml_temp.append('</Simulation>')
        xml_temp.append('</Experiment_plan>')

        xml = '\n'.join(xml_temp)

        # export xml
        if os.path.isdir(self.output_folder) is False:
            os.makedirs(self.output_folder)
        os.chdir(self.headless_folder)  # change working directory temporarily

        print(xml)
        f = open(xml_output_path, 'w')
        f.write(xml)
        f.close()

    def run_script(self, xml_path_):
        # run script
        if not xml_path_:
            xml_path = self.headless_folder + '/simulation_parameters.xml'
        else: xml_path = xml_path_
        command = self.script + " " + xml_path + " " + self.output_folder
        subprocess.call(command, shell=True)
        # self.open_and_call(command, session.handlers['data_view'].activate())

        os.chdir(self.cwd)  # return to previous cwd

        # TODO: wait until GAMA delivers outputs
        session.handlers['data_view'].activate()

    def open_and_call(self, popen_args, on_exit):

        def run_in_thread(on_exit, popen_args):
            proc = subprocess.Popen(popen_args, shell=True)
            proc.wait()
            on_exit()
            return

        thread = threading.Thread(target=run_in_thread, args=(on_exit, popen_args))
        thread.start()
        return thread