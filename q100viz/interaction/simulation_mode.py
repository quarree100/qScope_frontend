import pandas
import os
import subprocess
import threading
import pygame
import datetime
import random

import q100viz.session as session
from q100viz.settings.config import config
import q100viz.graphics.graphs as graphs

class SimulationMode:
    def __init__(self):
        self.name = 'simulation'

        self.cwd = os.getcwd()  # hold current working directory to return to later

        # simulation setup
        self.headless_folder = config['GAMA_HEADLESS_FOLDER']
        self.script = self.headless_folder + 'gama-headless.sh'
        self.current_output_folder = ''  # will be set in activate()
        self.xml_path = ''               # will be set in activate()
        self.final_step = None           # will be set in activate()
        self.max_year = 2045             # will be set in activate()
        self.output_folders = []         # list of output folders of all game rounds
        self.using_timestamp = True
        self.seed = 1.0

        self.matplotlib_neighborhood_images = {}

        self.xml = None

    def activate(self, max_year=None):

        session.environment['mode'] = self.name
        session.active_mode = self

        # increase round counter to globally log q-scope iterations:
        session.environment['current_iteration_round'] = (
            session.environment['current_iteration_round'] + 1) % session.num_of_rounds

        # derive final step from defined simulation runtime:
        if config['SIMULATION_FORCE_NUM_STEPS'] == 0:
            runtime = pandas.read_csv('../data/includes/csv-data_technical/initial_variables.csv',
                                      index_col='var').loc['model_runtime_string', 'value']
            if runtime == '2020-2030':
                self.final_step = 10 * 365 + 3  # include leapyears 2020, 2024, 2028, 2032, 2036, 2040, 2044
                self.max_year = 2030  # used by slider

            elif runtime == '2020-2040':
                self.final_step = 20 * 365 + 5
                self.max_year = 2040

            elif runtime == '2020-2045':
                self.final_step = 25 * 365 + 7
                self.max_year = 2045
        else:
            # overwrite final step if set via flag --sim_steps:
            self.final_step = config['SIMULATION_FORCE_NUM_STEPS']
            self.max_year = self.final_step / 365

        if max_year is not None:
            self.max_year = max_year
            self.final_step = ((max_year - 2020) * 365) + int((max_year - 2020)/4)

        self.model_file = os.path.normpath(
            os.path.join(self.cwd, config['GAMA_MODEL_FILE']))

        # display setup:
        for grid in session.grid_1, session.grid_2:
            for slider in grid.sliders.values():
                slider.show_text = False
                slider.show_controls = False
        session.show_basemap = False
        session.show_polygons = False

        session.api.send_session_env()

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
        # session.scenario_data[session.environment['active_scenario_handle']] = pandas.read_csv(
        #     '../data/scenario_{0}.csv'.format(session.environment['active_scenario_handle'])).set_index('name')

        # provide parameters:
        params = pandas.DataFrame(columns=['name', 'type', 'value', 'var'])
        params.loc[len(params)] = ['timestamp', 'STRING',
                                   self.timestamp, 'timestamp']

        # values to be used in trend model:
        params.loc[len(params)] = ['Alpha scenario', 'STRING',
                                   session.scenario_data[session.environment['active_scenario_handle']].loc['alpha_scenario', 'value'], 'alpha_scenario']
        params.loc[len(params)] = ['Carbon price scenario', 'STRING',
                                   session.scenario_data[session.environment['active_scenario_handle']].loc['carbon_price_scenario', 'value'], 'carbon_price_scenario']
        params.loc[len(params)] = ['Energy prices scenario', 'STRING',
                                   session.scenario_data[session.environment['active_scenario_handle']].loc['energy_price_scenario', 'value'], 'energy_price_scenario']
        params.loc[len(params)] = ['Q100 OpEx prices scenario', 'STRING',
                                   session.scenario_data[session.environment['active_scenario_handle']].loc['q100_price_opex_scenario', 'value'], 'q100_price_opex_scenario']
        params.loc[len(params)] = ['Q100 CapEx prices scenario', 'STRING',
                                   session.scenario_data[session.environment['active_scenario_handle']].loc['q100_price_capex_scenario', 'value'], 'q100_price_capex_scenario']
        params.loc[len(params)] = ['Q100 Emissions scenario', 'STRING',
                                   session.scenario_data[session.environment['active_scenario_handle']].loc['q100_emissions_scenario', 'value'], 'q100_emissions_scenario']
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

        ############### debug: select random of 100 buildings: ########
        if session.debug_num_of_random_buildings > 0:
            df = session.buildings.df.sample(
                n=session.debug_num_of_random_buildings)
            df['selected'] = True
            df['group'] = [random.randint(0, 3) for x in df.values]
            if session.debug_force_connect:
                df['connection_to_heat_grid'] = random.randint(2020, session.simulation.max_year)
            session.buildings.df.update(df)
            print("selecting random {0} buildings:".format(
                session.debug_num_of_random_buildings))

        ################# export buildings_clusters to csv ############
        clusters_outname = self.current_output_folder + '/buildings_clusters_{0}.csv'.format(str(
            self.timestamp)) if self.using_timestamp else '../data/output/buildings_clusters_{0}.csv'.format(str(self.timestamp))

        if not os.path.isdir(self.current_output_folder):
            os.makedirs(self.current_output_folder)

        selected_buildings = session.buildings.df[session.buildings.df.selected]
        selected_buildings[['spec_heat_consumption', 'spec_power_consumption', 'energy_source', 'electricity_supplier',
                            'connection_to_heat_grid', 'refurbished', 'save_energy']].to_csv(clusters_outname)

        # compose image paths as required by infoscreen
        session.gama_iteration_images[session.environment['current_iteration_round']] = [
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

        # send final_step to infoscreen:
        session.api.send_dataframe_as_json(pandas.DataFrame(data={"final_step": [self.final_step]}))

        # start simulation
        self.make_xml(params, outputs, self.xml_path,
                      self.final_step, None, 'agent_decision_making')
        self.run_script(self.xml_path)

        ####################### export matplotlib graphs #######################

        ########## individual buildings data ########
        for group_df in session.buildings.list_from_groups():
            if group_df is not None:
                for idx in group_df.index:

                    # export emissions graph:
                    graphs.export_using_columns(
                        csv_name="/emissions/CO2_emissions_{0}.csv".format(
                            idx),
                        search_in_folders=self.output_folders,
                        columns=['building_emissions'],
                        title_="CO2-Emissionen",
                        outfile=self.current_output_folder +
                        "/emissions/CO2_emissions_{0}.png".format(idx),
                        xlabel_="Jahr",
                        ylabel_="ø-Emissionen [$kg_{CO2,eq}$]",
                        x_='current_date',
                        convert_grams_to_kg=True
                    )

                    # export energy prices graph:
                    graphs.export_using_columns(
                        csv_name="/energy_prices/energy_prices_{0}.csv".format(
                            idx),
                        search_in_folders=self.output_folders,
                        columns=['building_expenses_heat',
                                 'building_expenses_power'],
                        labels_=['Wärmekosten', 'Stromkosten'],
                        outfile=self.current_output_folder +
                        "/energy_prices/energy_prices_{0}.png".format(idx),
                        title_="Energiekosten",
                        xlabel_="Jahr",
                        ylabel_="Energiekosten [€/Monat]",
                        x_='current_date'
                    )

                    # pass path to buildings in infoscreen-compatible format
                    group_df.at[idx, 'emissions_graphs'] = str(os.path.normpath(
                        'data/outputs/output_{0}/emissions/CO2_emissions_{1}.png'.format(self.timestamp, idx)))
                    group_df.at[idx, 'energy_prices_graphs'] = str(os.path.normpath(
                        'data/outputs/output_{0}/energy_prices/energy_prices_{1}.png'.format(self.timestamp, idx)))
                session.buildings.df.update(group_df)

        ############# neighborhood data #############
        # combined emissions graph for selected buildings:
        graphs.export_combined_emissions(
            session.buildings.list_from_groups(),
            self.current_output_folder,
            self.current_output_folder + "/emissions/CO2_emissions_groups.png"
            )

        # combined energy prices graph for selected buildings:
        graphs.export_combined_energy_prices(
            self.current_output_folder,
            outfile=self.current_output_folder + "/energy_prices/energy_prices_groups.png")

        # neighborhood total emissions:
        graphs.export_using_columns(
            csv_name="/emissions/CO2_emissions_neighborhood.csv",
            search_in_folders=self.output_folders,
            columns=['emissions_neighborhood_accu'],
            title_="kumulierte Gesamtemissionen des Quartiers",
            outfile=self.current_output_folder + "/emissions/CO2_emissions_neighborhood.png",
            xlabel_="Jahr",
            ylabel_="CO2 [$kg_{eq}$]",
            x_='current_date',
            convert_grams_to_kg=True
        )

        # neighborhood total energy prices prognosis:
        graphs.export_using_columns(
            csv_name="/energy_prices/energy_prices_total.csv",
            search_in_folders=self.output_folders,
            columns=['power_price', 'oil_price', 'gas_price'],
            labels_=['Strompreis', 'Ölpreis', 'Gaspreis'],
            title_="Energiepreis",
            outfile=self.current_output_folder + "/energy_prices/energy_prices_total.png",
            xlabel_="Jahr",
            ylabel_="Preis [ct/kWh]",
            x_='current_date'
        )

        # define titles for images and their location
        self.matplotlib_neighborhood_images = {
            "emissions_neighborhood_accu": "data/outputs/output_{0}/emissions/CO2_emissions_neighborhood.png".format(str(self.timestamp)),
            "energy_prices": "data/outputs/output_{0}/energy_prices/energy_prices_total.png".format(str(self.timestamp)),
            "emissions_groups": "data/outputs/output_{0}/emissions/CO2_emissions_groups.png".format(str(self.timestamp)),
            "energy_prices_groups": "data/outputs/output_{0}/energy_prices/energy_prices_groups.png".format(str(self.timestamp))
        }

        # send matplotlib created images to infoscreen
        session.environment['neighborhood_images'] = self.matplotlib_neighborhood_images
        # session.api.send_dataframe_as_json(selected_buildings)

        ########################### csv export ########################

        # compose csv paths for infoscreen to make graphs
        session.emissions_data_paths[session.environment['current_iteration_round']] = [
            str(os.path.normpath('data/outputs/output_{0}/emissions/{1}'.format(self.timestamp, file_name))) for file_name in os.listdir('../data/outputs/output_{0}/emissions'.format(str(self.timestamp)))
        ]

        ## send GAMA image paths to infoscreen (per iteration round!) #
        dataview_wrapper = ['' for i in range(session.num_of_rounds)]
        for i in range(session.num_of_rounds):
            images_and_data = {'iteration_round': i,
                               'gama_iteration_images': session.gama_iteration_images[i],
                               'emissions_data_paths': session.emissions_data_paths[i]
                               }

            dataview_wrapper[i] = images_and_data
        dataview_wrapper = {
            'data_view_neighborhood_data': [dataview_wrapper]
        }

        data_view_neighborhood_df = pandas.DataFrame(data=dataview_wrapper)
        session.api.send_dataframe_as_json(data_view_neighborhood_df)

        # TODO: wait until GAMA delivers outputs
        session.individual_data_view.activate()

    ########################### frontend input ########################
    def process_event(self, event):
        if event.type == pygame.locals.MOUSEBUTTONDOWN:
            session.grid_1.mouse_pressed(event.button)
            session.grid_2.mouse_pressed(event.button)
            session.flag_export_canvas = True

            self.process_grid_change()

    ############################# grid changes ########################
    def process_grid_change(self):
        for grid in [session.grid_1, session.grid_2]:
            for y, row in enumerate(grid.grid):
                for x, cell in enumerate(row):
                    if cell.selected:
                        pass

        session.api.send_simplified_dataframe_with_environment_variables(
            session.buildings.df[session.buildings.df.selected], session.environment)

    def update(self):

        pass

    ################################ draw #############################
    def draw(self, canvas):
        if session.VERBOSE_MODE:
            font = pygame.font.SysFont('Arial', 40)
            canvas.blit(font.render("Berechne Energiekosten und Emissionen...", True, (255, 255, 255)),
                        (session.canvas_size[0]/4, session.canvas_size[1]/2))

        if len(session.buildings.df[session.buildings.df.selected]):
            # highlight selected buildings
            session._gis.draw_polygon_layer(
                canvas,
                session.buildings.df[session.buildings.df.selected], 2, (
                    255, 0, 127)
            )

    ########################### script: prepare #######################
    def make_xml(self, parameters, outputs, xml_output_path, finalStep=None, until=None, experiment_name=None):

        # header
        xml_temp = ['<Experiment_plan>']
        xml_temp.append('  <Simulation experiment="{0}" sourcePath="{1}" finalStep="{2}"'.format(
            str(experiment_name), str(self.model_file), str(finalStep)))
        if self.seed is not None:
            xml_temp.append('seed="{0}"'.format(str(self.seed)))
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

    ########################### script: run ###########################
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
        # self.open_and_call(command, session.individual_data_view.activate())

        os.chdir(self.cwd)  # return to previous cwd

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
