''' Simulation Mode fakes parameter changes for buildings later done by the ABM'''

from operator import index
from time import strftime
import pandas
import os
import subprocess
import threading
from matplotlib import pyplot as plt
import pygame
import datetime
import random

import q100viz.session as session
from q100viz.settings.config import config


class SimulationMode:
    def __init__(self):
        self.name = 'simulation'

        self.cwd = os.getcwd()  # hold current working directory to return to later

        # simulation setup
        self.headless_folder = config['GAMA_HEADLESS_FOLDER']
        self.script = self.headless_folder + 'gama-headless.sh'
        self.model_file = os.path.normpath(
            os.path.join(self.cwd, config['GAMA_MODEL_FILE']))
        self.current_output_folder = ''  # will be set in activate()
        self.xml_path = ''               # will be set in activate()
        self.final_step = None           # will be set in activate()
        self.output_folders = []         # list of output folders of all game rounds
        self.using_timestamp = True

        self.xml = None

    def activate(self):
        self.final_step = config['SIMULATION_NUM_STEPS']

        session.environment['mode'] = self.name
        session.active_handler = self

        # display setup:
        for slider in session.grid_1.slider, session.grid_2.slider:
            slider.show_text = False
            slider.show_controls = False
        session.show_basemap = False
        session.show_polygons = False

        # simulation start time
        self.timestamp = str(
            datetime.datetime.now().strftime("%Y%m%d_%H-%M-%S"))

        # set output folder:
        if self.using_timestamp:
            self.current_output_folder = os.path.normpath(os.path.join(
                self.cwd, config['GAMA_OUTPUT_FOLDER'] + '_' + self.timestamp))
        else:
            self.current_output_folder = os.path.normpath(
                os.path.join(self.cwd, config['GAMA_OUTPUT_FOLDER']))
        self.xml_path = self.current_output_folder + \
            '/simulation_parameters_' + self.timestamp + '.xml'

        self.output_folders.append(self.current_output_folder)

        # load parameters from csv file:
        scenario_df = pandas.read_csv(
            '../data/scenario_{0}.csv'.format(session.environment['active_scenario'])).set_index('name')

        # provide parameters:
        params = pandas.DataFrame(columns=['name', 'type', 'value', 'var'])
        params.loc[len(params)] = ['timestamp', 'STRING',
                                   self.timestamp, 'timestamp']

        # values to be used in trend model:
        params.loc[len(params)] = ['Alpha scenario', 'STRING',
                                   scenario_df.loc['alpha_scenario', 'value'], 'alpha_scenario']
        params.loc[len(params)] = ['Carbon price scenario', 'STRING',
                                   scenario_df.loc['carbon_price_scenario', 'value'], 'carbon_price_scenario']
        params.loc[len(params)] = ['Energy prices scenario', 'STRING',
                                   scenario_df.loc['energy_price_scenario', 'value'], 'energy_price_scenario']
        params.loc[len(params)] = ['Q100 OpEx prices scenario', 'STRING',
                                   scenario_df.loc['q100_price_opex_scenario', 'value'], 'q100_price_opex_scenario']
        params.loc[len(params)] = ['Q100 CapEx prices scenario', 'STRING',
                                   scenario_df.loc['q100_price_capex_scenario', 'value'], 'q100_price_capex_scenario']
        params.loc[len(params)] = ['Q100 Emissions scenario', 'STRING',
                                   scenario_df.loc['q100_emissions_scenario', 'value'], 'q100_emissions_scenario']
        params.loc[len(params)] = ['Carbon price for households?',
                                   'BOOLEAN', 'false', 'carbon_price_on_off']
        # TODO:
        # params.loc[len(params)] = ['keep_seed', 'bool', 'true']

        # provide outputs:
        outputs = pandas.DataFrame(columns=['id', 'name', 'framerate'])
        outputs.loc[len(outputs)] = ['0', 'neighborhood',
                                     str(self.final_step - 1)]
        outputs.loc[len(outputs)] = [
            '1', 'households_employment_pie', str(self.final_step - 1)]
        outputs.loc[len(outputs)] = ['2', 'Charts', str(self.final_step - 1)]
        outputs.loc[len(outputs)] = ['3', 'Modernization',
                                     str(self.final_step - 1)]
        outputs.loc[len(outputs)] = ['4', 'Monthly Emissions',
                                     str(self.final_step - 1)]
        outputs.loc[len(outputs)] = [
            '5', 'Emissions cumulative', str(self.final_step - 1)]

        # export buildings_clusters to csv
        clusters_outname = self.current_output_folder + '/buildings_clusters_{0}.csv'.format(str(
            self.timestamp)) if self.using_timestamp else '../data/output/buildings_clusters_{0}.csv'.format(str(self.timestamp))

        print(clusters_outname)

        if not os.path.isdir(self.current_output_folder):
            os.makedirs(self.current_output_folder)

        # debug: select random of 100 buildings:
        if session.DEBUG_MODE:
            df = session.buildings.sample(n=random.randint(10, 100))
            df['selected'] = True
            df['group'] = [random.randint(0, 3) for x in df.values]
            if session.debug_connect:
                df['connected'] = True
            session.buildings.update(df)
            session.print_full_df(session.buildings)

        df = session.buildings[session.buildings.selected]
        df[['spec_heat_consumption', 'spec_power_consumption', 'energy_source', 'electricity_supplier',
            'connection_to_heat_grid', 'refurbished', 'environmental_engagement']].to_csv(clusters_outname)

        # compose image paths as required by infoscreen
        session.iteration_images[session.iteration_round] = [
            str(os.path.normpath('data/outputs/output_{0}/snapshot/Chartsnull-{1}.png'.format(
                self.timestamp, str(self.final_step - 1)))),
            str(os.path.normpath('data/outputs/output_{0}/snapshot/Emissions cumulativenull-{1}.png'.format(
                self.timestamp, str(self.final_step - 1)))),
            str(os.path.normpath('data/outputs/output_{0}/snapshot/Monthly Emissionsnull-{1}.png'.format(
                self.timestamp, str(self.final_step - 1)))),
            str(os.path.normpath('data/outputs/output_{0}/snapshot/households_employment_pienull-{1}.png'.format(
                self.timestamp, str(self.final_step - 1)))),
            str(os.path.normpath('data/outputs/output_{0}/snapshot/Modernizationnull-{1}.png'.format(
                self.timestamp, str(self.final_step - 1)))),
            str(os.path.normpath('data/outputs/output_{0}/snapshot/neighborhoodnull-{1}.png'.format(
                self.timestamp, str(self.final_step - 1))))
        ]

        # start simulation
        self.make_xml(params, outputs, self.xml_path,
                      self.final_step, None, 'agent_decision_making')
        self.run_script(self.xml_path)

        self.export_graphs(
            csv_name="/emissions/CO2_emissions_neighborhood.csv",
            columns=['emissions_neighborhood_accu'],
            title_="akkumulierte Gesamtemissionen des Quartiers",
            xlabel_="Datum",
            ylabel_="Gesamte Emissionen [gCO2]",
            x_='current_date'
        )

        self.export_graphs(
            csv_name="/energy_prices/energy_prices_total.csv",
            columns=['power_price', 'oil_price', 'gas_price'],
            labels_=['Energiepreis', 'Ölpreis', 'Gaspreis'],
            title_="Energiekosten",
            xlabel_="Datum",
            ylabel_="Kosten [€]",
            x_='current_date'
        )
        # compose csv paths for infoscreen to make graphs
        session.emissions_data_paths[session.iteration_round] = [
            str(os.path.normpath('data/outputs/output_{0}/emissions/{1}'.format(self.timestamp, file_name))) for file_name in os.listdir('../data/outputs/output_{0}/emissions'.format(str(self.timestamp)))
        ]

        # send image paths to infoscreen
        dataview_wrapper = ['' for i in range(session.num_of_rounds)]
        for i in range(session.num_of_rounds):
            images_and_data = {'iteration_round': i,
                               'iteration_images': session.iteration_images[i],
                               'emissions_data_paths': session.emissions_data_paths[i]
                               }

            dataview_wrapper[i] = images_and_data
        dataview_wrapper = {
            'data_view_data': [dataview_wrapper]
        }

        df = pandas.DataFrame(data=dataview_wrapper)
        session.api.send_dataframe_as_json(df)

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

        session.api.send_simplified_dataframe_with_environment_variables(
            session.buildings[session.buildings.selected], session.environment)

    def update(self):

        pass

    def draw(self, canvas):
        if session.VERBOSE_MODE:
            font = pygame.font.SysFont('Arial', 40)
            canvas.blit(font.render("Simulation is running...", True, (255, 255, 255)),
                        (session.canvas_size[0]/2, session.canvas_size[1]/2))

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
        xml_temp.append('  <Simulation experiment="{0}" sourcePath="{1}" finalStep="{2}"'.format(
            str(experiment_name), str(self.model_file), str(finalStep)))
        if seed is not None:
            xml_temp.append('seed="{0}"'.format(str(seed)))
        if until is not None:
            xml_temp.append('until="{0}"'.format(str(until)))
        xml_temp.append('>')

        # parameters
        xml_temp.append('  <Parameters>')
        for index, row in parameters.iterrows():
            xml_temp.append('    <Parameter name="{0}" type="{1}" value="{2}" var="{3}"/>'.format(
                row['name'], row['type'], row['value'], row['var']))
        xml_temp.append('  </Parameters>')

        # outputs
        xml_temp.append('  <Outputs>')
        for index, row in outputs.iterrows():
            xml_temp.append('    <Output id="{0}" name="{1}" framerate="{2}" />'.format(
                row['id'], row['name'], row['framerate']))
        xml_temp.append('  </Outputs>')
        xml_temp.append('</Simulation>')
        xml_temp.append('</Experiment_plan>')

        xml = '\n'.join(xml_temp)

        # export xml
        if os.path.isdir(self.current_output_folder) is False:
            os.makedirs(self.current_output_folder)
        os.chdir(self.headless_folder)  # change working directory temporarily

        # print(xml)
        f = open(xml_output_path, 'w')
        f.write(xml)
        f.close()

    def run_script(self, xml_path_):
        # run script
        if not xml_path_:
            xml_path = self.current_output_folder + \
                '/simulation_parameters_' + str(self.timestamp) + '.xml'
        else:
            xml_path = xml_path_
        command = self.script + " " + xml_path + " " + self.current_output_folder

        sim_start = datetime.datetime.now()
        subprocess.call(command, shell=True)
        print("simulation finished. duration = ",
              datetime.datetime.now() - sim_start)
        # self.open_and_call(command, session.handlers['data_view_individual'].activate())

        os.chdir(self.cwd)  # return to previous cwd

        # TODO: wait until GAMA delivers outputs
        session.handlers['data_view_individual'].activate()

    def open_and_call(self, popen_args, on_exit):

        def run_in_thread(on_exit, popen_args):
            proc = subprocess.Popen(popen_args, shell=True)
            proc.wait()
            on_exit()
            return

        thread = threading.Thread(
            target=run_in_thread, args=(on_exit, popen_args))
        thread.start()
        return thread

    def export_graphs(self, csv_name, columns, x_, title_="", xlabel_="", ylabel_="", labels_=None):
        '''exports specified column of csv-data-file for every iteration round to graph and exports png'''

        # read exported results:
        rounds_data = []

        # looks for all files with specified csv_name:
        for output_folder in self.output_folders:
            rounds_data.append(pandas.read_csv(output_folder + csv_name))

        plt.figure(figsize=(16, 9))  # inches
        it_round = 0
        for df in rounds_data:
            col_num = 0
            for column in columns:
                label_ = 'Durchlauf {0}'.format(
                    it_round+1) if labels_ == None else '{0} (Durchlauf {1})'.format(labels_[col_num], it_round+1)

                # lower brightness for each round:
                color_ = (
                    session.quarree_colors_float[col_num % len(
                        columns)][0]/(1+it_round*0.33),  # r, float
                    session.quarree_colors_float[col_num % len(
                        columns)][1]/(1+it_round*0.33),  # g, float
                    session.quarree_colors_float[col_num % len(
                        columns)][2]/(1+it_round*0.33),  # b, float
                )

                # plot:
                df.plot(
                    kind='line',
                    x=x_,
                    y=column,
                    label=label_,
                    color=color_,
                    ax=plt.gca())

                col_num += 1

            it_round += 1

        plt.title(title_)
        plt.xlabel(xlabel_)
        plt.ylabel(ylabel_)
        plt.xticks(rotation=270, fontsize=8)

        plt.savefig(self.current_output_folder + "/{0}.png".format(title_))
