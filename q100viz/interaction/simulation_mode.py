import time
import pandas
import os
import subprocess
import threading
import pygame
import datetime
import random
import json

import q100viz.session as session
from q100viz.settings.config import config
import q100viz.graphics.graphs as graphs
from q100viz.devtools import devtools as devtools
class SimulationMode:
    def __init__(self):
        self.name = 'simulation'
        self.activation_buffer_time = 4  # seconds before simulation begins

        self.running = False
        self.progress = "0%"

        self.cwd = os.getcwd()  # hold current working directory to return to later

        # simulation setup
        self.headless_folder = config['GAMA_HEADLESS_FOLDER']
        self.reference_data_folder = os.path.normpath(
            os.path.join(self.cwd, config['REFERENCE_DATA_FOLDER']))
        self.script = self.headless_folder + 'gama-headless.sh'
        self.current_output_folder = ''  # will be set in setup()
        self.xml_path = ''               # will be set in setup()
        self.final_step = 0              # will be set in setup()
        self.max_year = 2045             # will be set in setup()
        self.output_folders = []         # list of output folders of all game rounds
        # game start time
        self.timestamp = str(
            datetime.datetime.now().strftime("%Y%m%d_%H-%M-%S"))
        self.output_folder = os.path.normpath(os.path.join(
                self.cwd, config['GAMA_OUTPUT_FOLDER'] + '_' + self.timestamp))

        self.seed = 1.0

        self.matplotlib_neighborhood_images = {}
        self.export_neighborhood_graphs_only = False

        self.xml = None

    def activate(self):
        '''do not call! This function is automatically called in main loop. Instead, enable a mode by setting session.active_mode = session.[mode]'''

        session.environment['mode'] = self.name
        for mode in session.modes:
            mode.waiting_to_start = False

        self.progress = "0%"

        # disable interface:
        for grid in session.grid_1, session.grid_2:
            for slider in grid.sliders.values():
                slider.show_text = False
                slider.show_controls = False
        # show GIS layer:
        session.show_basemap = True
        session.show_polygons = True

        session.api.send_session_env()

        # start simulation:
        self.running = True
        simulation_thread = threading.Thread(target=session.simulation.run, args=[devtools.test_run], daemon=True)
        simulation_thread.start()

    ################### SIMULATION SETUP FUNCTION #####################

    def setup(self, input_max_year=None, export_neighborhood_graphs_only=False, export_graphs=True):

        self.export_neighborhood_graphs_only = export_neighborhood_graphs_only  # disable export of individual graphs, for debugging purposes
        self.flag_create_graphs = export_graphs

        # --------------------- final simulation step -----------------
        # derive final step from defined simulation runtime:
        if config['SIMULATION_FORCE_END_YEAR'] == 0:
            runtime = pandas.read_csv('../data/includes/csv-data_technical/initial_variables.csv',
                                      index_col='var').loc['model_runtime_string', 'value']
            self.max_year = int(runtime[-4:])  # last four digits of model_runtime_string
            self.final_step = ((self.max_year + 1 - 2020) * 365) + int((self.max_year - 2020)/4) # num of days including leapyears 2020, 2024, 2028, 2032, 2036, 2040, 2044
        else:
            # overwrite final step if set via flag --sim_steps:
            self.max_year = config['SIMULATION_FORCE_END_YEAR']
            self.final_step = ((self.max_year + 1 - 2020) * 365) + int((self.max_year - 2020)/4)
        # overwrite by function input:
        if input_max_year is not None:
            self.max_year = min(input_max_year + 1, 2046)
            self.final_step = ((self.max_year - 2020) * 365) + int((self.max_year - 2020)/4) # num of days including leapyears 2020, 2024, 2028, 2032, 2036, 2040, 2044

        print('simulation will run until {0}-12-31 ({1} steps)'.format(self.max_year-1, self.final_step))

        # increase round counter to globally log q-scope iterations:
        session.environment['current_iteration_round'] = (
            session.environment['current_iteration_round'] + 1) % session.num_of_rounds

        # ------------------------- model file setup ------------------
        self.model_file = os.path.normpath(
            os.path.join(self.cwd, config['GAMA_MODEL_FILE']))

        # --------------------- set output folder: --------------------
        self.current_output_folder = os.path.normpath(self.output_folder + '/round' + str(session.environment['current_iteration_round']))
        self.xml_path = self.current_output_folder + \
            '/simulation_parameters_' + self.timestamp + '.xml'

        self.output_folders.append(self.current_output_folder)

        # -------------------------- model input data -----------------

        # load parameters from csv file:
        # session.scenario_data[session.environment['active_scenario_handle']] = pandas.read_csv(
        #     '../data/scenario_{0}.csv'.format(session.environment['active_scenario_handle'])).set_index('name')

        # provide parameters:
        params = pandas.DataFrame(columns=['name', 'type', 'value', 'var'])

        # timestamp and round define output folder:
        params.loc[len(params)] = ['timestamp', 'STRING',
                                   self.timestamp, 'timestamp']
        params.loc[len(params)] = ['round', 'STRING',
                                   session.environment['current_iteration_round'], 'round']

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

        # model outputs:
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
            connection_date = random.randint(2020, self.max_year) if session.debug_connection_date > 0 else False
            devtools.mark_random_buildings_for_simulation(session.buildings.df, session.debug_num_of_random_buildings, connection_to_heat_grid=connection_date, refurbished=session.debug_refurb_year, save_energy=session.debug_force_save_energy)

        session.api.send_message(json.dumps(session.buildings.get_dict_with_api_wrapper()))

        ################# export buildings_clusters to csv ############
        clusters_outname = self.current_output_folder + '/buildings_clusters_{0}.csv'.format(str(self.timestamp))  # TODO: remove timestamp

        if not os.path.isdir(self.current_output_folder):
            os.makedirs(self.current_output_folder)

        # filter already selected buildings from list:
        try:
            session.scenario_selected_buildings = session.scenario_selected_buildings[session.scenario_selected_buildings['group'] < 0]
            for group_df in session.buildings.list_from_groups():
                if group_df is not None:
                    for idx in group_df.index:
                        if idx in session.scenario_selected_buildings.index:
                            session.scenario_selected_buildings = session.scenario_selected_buildings.drop(idx)
        except Exception as e:
            print("cannot filter scenario list", e)
            devtools.log += "\nCannot filter scenario list: %s" % e

        selected_buildings = pandas.concat([session.buildings.df[session.buildings.df.selected], session.scenario_selected_buildings])
        selected_buildings[['spec_heat_consumption', 'spec_power_consumption', 'energy_source', 'connection_to_heat_grid', 'refurbished', 'save_energy', 'group']].to_csv(clusters_outname)

        # send final_step to infoscreen:
        session.api.send_dataframe_as_json(pandas.DataFrame(data={"final_step": [self.final_step]}))

        # start simulation
        self.make_xml(params, outputs, self.xml_path,
                      self.final_step, None, 'agent_decision_making')

        self.running = True

    ######################## SIMULATION RUN THREAD ####################

    def run(self, test_run=False):
        while not self.running:
            time.sleep(1)
            if threading.current_thread().__class__.__name__ == '_MainThread':
                print("Simulation was not set up yet! call simulation.setup() before running.")
                return

        self.running = False

        # update building images with reference data for discussion:
        if session.environment['current_iteration_round'] == 0:
            for idx in session.buildings.df.index:
                session.buildings.df.at[idx, 'emissions_graphs'] = "../data/precomputed/simulation_defaults/emissions/CO2_emissions_{0}.png".format(idx)
                session.buildings.df.at[idx, 'energy_prices_graphs'] = "../data/precomputed/simulation_defaults/energy_prices/energy_prices_{0}.png".format(idx)
            session.api.send_message(json.dumps(session.buildings.get_dict_with_api_wrapper()))

        self.run_script(self.xml_path)
        session.api.send_message(json.dumps({'step' : self.final_step-1}))  # simulation done

        if self.flag_create_graphs:
            try:
                self.export_graphs()
            except Exception as e:
                print("cannot export graphs", e)
                devtools.log += "\nCannot export graphs: %s" % e

        # define titles for images and their location
        self.matplotlib_neighborhood_images = {
            "emissions_neighborhood_accu": "data/outputs/output_{0}/round{1}/emissions/CO2_emissions_neighborhood.png".format(str(self.timestamp), session.environment['current_iteration_round']),
            "energy_prices": "data/outputs/output_{0}/round{1}/energy_prices/energy_prices_total.png".format(str(self.timestamp), session.environment['current_iteration_round']),
            "emissions_groups": "data/outputs/output_{0}/round{1}/emissions/CO2_emissions_groups.png".format(str(self.timestamp), session.environment['current_iteration_round']),
            "energy_prices_groups": "data/outputs/output_{0}/round{1}/energy_prices/energy_prices_groups.png".format(str(self.timestamp), session.environment['current_iteration_round'])
        }

        # send matplotlib created images to infoscreen
        session.environment['neighborhood_images'] = self.matplotlib_neighborhood_images

        ########################### csv export ########################

        # compose csv paths for infoscreen to make graphs
        session.emissions_data_paths[session.environment['current_iteration_round']] = [
            str(
                os.path.normpath(self.current_output_folder[self.current_output_folder.find('data'):] + '/emissions/{1}'.format(session.environment['current_iteration_round'], file_name)))
                for file_name in os.listdir(self.current_output_folder + '/emissions')
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

        session.active_mode = session.individual_data_view  # marks total_data_view_mode to be started in main thread

    ########################### frontend input ########################
    def process_event(self, event):
        if event.type == pygame.locals.MOUSEBUTTONDOWN:
            session.grid_1.mouse_pressed(event.button)
            session.grid_2.mouse_pressed(event.button)
            session.flag_export_canvas = True

            self.process_grid_change()

    ############################# grid changes ########################
    def process_grid_change(self):
        pass

    def update(self):
        pass

    ################################ draw #############################
    def draw(self, canvas):
        # font = pygame.font.SysFont('Arial', 40)
        # canvas.blit(font.render("Berechne Energiekosten und Emissionen...", True, (255, 255, 255)),
        #             (session.canvas_size[0]/4, session.canvas_size[1]/2))

        try:
            # highlight selected buildings (draws colored stroke on top)
            if len(session.buildings.df[session.buildings.df.selected]):

                sel_buildings = session.buildings.df[(session.buildings.df.selected)]
                for building in sel_buildings.to_dict('records'):
                    fill_color = pygame.Color(session.user_colors[int(building['group'])])

                    points = session._gis.surface.transform(building['geometry'].exterior.coords)
                    pygame.draw.polygon(session._gis.surface, fill_color, points, 2)

        except Exception as e:
                print("Cannot draw frontend:", e)
                devtools.log += "\nCannot draw frontend: %s" % e

        font = pygame.font.SysFont('Arial', 18)
        nrows = 22

        column = 20
        row = 17
        font = pygame.font.SysFont('Arial', 18)
        canvas.blit(font.render(
            session.simulation.progress, True, pygame.Color(255,255,255)),
            (session.grid_2.rects_transformed[column+nrows*row][1][0][0] + 5,
            session.grid_2.rects_transformed[column+nrows*row][1][0][1] + 10)
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
        print("simulation starting using model file", self.model_file)
        subprocess.call(command, shell=True)
        print("simulation finished. duration = ",
              datetime.datetime.now() - sim_start)

        os.chdir(self.cwd)  # return to previous cwd

        ####################### export matplotlib graphs #######################

    def export_graphs(self):

        ############# neighborhood data #############
        # combined emissions graph for selected buildings:
        graphs.export_compared_emissions(
            session.buildings.list_from_groups(),
            self.current_output_folder,
            self.current_output_folder + "/emissions/CO2_emissions_groups.png"
            )

        # combined energy prices graph for selected buildings:
        graphs.export_compared_energy_costs(
            search_in_folder=self.current_output_folder,
            outfile=self.current_output_folder + "/energy_prices/energy_prices_groups.png")

        # neighborhood total emissions:
        # graphs.export_individual_emissions(
        #     csv_name="/emissions/CO2_emissions_neighborhood.csv",
        #     data_folders=self.output_folders,
        #     columns=['emissions_neighborhood_accu'],
        #     title_="jährlich kumulierte Gesamtemissionen des Quartiers",
        #     outfile=self.current_output_folder + "/emissions/CO2_emissions_neighborhood.png",
        #     xlabel_="Jahr",
        #     ylabel_="$CO_{2}$-Äquivalente (t)",
        #     x_='current_date',
        #     convert_grams_to_tons=True,
        #     compare_data_folder=self.current_output_folder + "/../../../precomputed/simulation_defaults"
        # )
        graphs.export_neighborhood_emissions_connections(
            emissions_file=self.current_output_folder + "/emissions/CO2_emissions_neighborhood.csv",
            emissions_compare_file=self.reference_data_folder + "/emissions/CO2_emissions_neighborhood.csv",
            connections_file=self.current_output_folder + "/connections/connections_export.csv",
            outfile=self.current_output_folder + "/emissions/CO2_emissions_neighborhood.png"
        )

        # neighborhood total energy prices prognosis:
        graphs.export_neighborhood_total_data(
            csv_name="/energy_prices/energy_prices_total.csv",
            data_folders=[self.current_output_folder],
            columns=['gas_price', 'power_price', 'oil_price'],
            labels_=['Gaspreis', 'Strompreis', 'Ölpreis',],
            title_="generelle Energiepreise nach Energieträger",
            outfile=self.current_output_folder + "/energy_prices/energy_prices_total.png",
            xlabel_="Jahr",
            ylabel_="Preis (ct/kWh)",
            x_='current_date',
            label_show_iteration_round=False,
            prepend_data=self.output_folder + "/../../data_pre-simulation/energy-prices_hh_2011-2022.csv"
            # compare_data_folder=self.current_output_folder + "/../../../precomputed/simulation_defaults"
        )

        ########## individual buildings data ########
        if self.export_neighborhood_graphs_only:
            return

        for group_df in session.buildings.list_from_groups():
            if group_df is None:
                continue

            for idx in group_df.index:
                # export emissions graph:
                graphs.export_individual_emissions(
                    csv_name="/emissions/CO2_emissions_{0}.csv".format(
                        idx),
                    data_folders=self.output_folders,
                    columns=['building_household_emissions'],
                    title_="Emissionen",
                    outfile=self.current_output_folder +
                    "/emissions/CO2_emissions_{0}.png".format(idx),
                    xlabel_="Jahr",
                    ylabel_="$CO_{2}$-Äquivalente (kg/Monat)",  # TODO: t/Jahr
                    x_='current_date',
                    convert_grams_to_kg=True,
                    compare_data_folder=self.current_output_folder + "/../../../precomputed/simulation_defaults",
                    figtext=
                        str(idx) + " "
                        + str(group_df.loc[idx, 'address']) + " "
                        + str(group_df.loc[idx, 'type'])
                        + "\nø-spez. Wärmeverbrauch: "
                        + str(group_df.loc[idx, 'spec_heat_consumption'])
                        + ", ø-spez. Stromverbrauch: "
                        + str(group_df.loc[idx, 'spec_heat_consumption'])
                        if devtools.VERBOSE_MODE else "",
                    figsize=(16,12),  # inches
                )

                # export energy prices graph:
                graphs.export_individual_energy_expenses(
                    building_idx = idx,
                    csv_name="/energy_prices/energy_prices_{0}.csv".format(
                        idx),
                    data_folders=self.output_folders,
                    columns=['building_household_expenses_heat',
                            'building_household_expenses_power'],
                    labels_=['Wärmekosten', 'Stromkosten'],
                    outfile=self.current_output_folder +
                    "/energy_prices/energy_prices_{0}.png".format(idx),
                    title_="Energiekosten pro Haushalt",
                    xlabel_="Jahr",
                    ylabel_="€/Monat",
                    x_='current_date',
                    compare_data_folder=self.current_output_folder + "/../../../precomputed/simulation_defaults",
                    figtext=
                        str(idx) + " "
                        + str(group_df.loc[idx, 'address']) + " "
                        + str(group_df.loc[idx, 'type'])
                        + "\nø-spez. Wärmeverbrauch: "
                        + str(group_df.loc[idx, 'spec_heat_consumption'])
                        + ", ø-spez. Stromverbrauch: "
                        + str(group_df.loc[idx, 'spec_heat_consumption'])
                        if devtools.VERBOSE_MODE else "",
                    figsize=(16,12),  # inches
                    prepend_historic_data=True,
                )

                # pass path to buildings in infoscreen-compatible format
                group_df.at[idx, 'emissions_graphs'] = str(
                    os.path.normpath(
                       session.simulation.current_output_folder[session.simulation.current_output_folder.find('data'):]
                    + '/emissions/CO2_emissions_{0}.png').format(idx))
                group_df.at[idx, 'energy_prices_graphs'] = str(
                   session.simulation.current_output_folder[session.simulation.current_output_folder.find('data'):]
                    + '/energy_prices/energy_prices_{0}.png'.format(idx))

                session.buildings.df.update(group_df)