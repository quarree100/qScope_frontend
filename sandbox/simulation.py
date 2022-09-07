import pandas
import os
import subprocess
import threading
from matplotlib import pyplot as plt
import pygame
import datetime
import random
from buildings import buildings_df

config = {
    # GIS files
    'BASEMAP_FILE': "../../data/GIS/Layer/180111-QUARREE100-RK_modifiziert_smaller.jpg",
    'GEBAEUDE_BESTAND_FILE': "../../data/GIS/Shapefiles/bestandsgebaeude_export.shp",
    'GEBAEUDE_NEUBAU_FILE': "../../data/GIS/Shapefiles/Neubau Gebaeude Kataster.shp",
    'WAERMESPEICHER_FILE': "../../data/GIS/Shapefiles/Waermespeicher.shp",
    'HEIZZENTRALE_FILE': "../../data/GIS/Shapefiles/Heizzentrale.shp",
    'NAHWAERMENETZ_FILE': "../../data/GIS/Shapefiles/Nahwaermenetz.shp",
    'TYPOLOGIEZONEN_FILE': "../../data/GIS/Shapefiles/Typologiezonen.shp",

    # graphics setup
    'SAVED_KEYSTONE_FILE': 'keystone.save',
    'SAVED_BUILDINGS_FILE': 'export/buildings_export.shp',

    # simulation files
    'GAMA_HEADLESS_FOLDER' : '/opt/gama-platform/headless/',
    'GAMA_OUTPUT_FOLDER': '../../data/outputs/output',
    'GAMA_MODEL_FILE' : '../../q100_abm_qscope-workshop/q100/models/qscope_ABM.gaml',
    'SIMULATION_NUM_STEPS' : 9496,

    # grid setup
    'CSPY_SETTINGS_FILE': '../../data/cityscopy.json',
    'GRID_1_SETUP_FILE': 'q100viz/settings/buildings_interaction_grid_1.csv',
    'GRID_2_SETUP_FILE': 'q100viz/settings/buildings_interaction_grid_2.csv',
    'GRID_1_INPUT_SCENARIOS_FILE': 'q100viz/settings/buildings_interaction_grid_1.csv',
    'GRID_2_INPUT_SCENARIOS_FILE': 'q100viz/settings/buildings_interaction_grid_2.csv',
    'GRID_1_INDIVIDUAL_DATA_VIEW_FILE': 'q100viz/settings/individual_data_view_grid_1.csv',
    'GRID_2_INDIVIDUAL_DATA_VIEW_FILE': 'q100viz/settings/individual_data_view_grid_2.csv',
    'GRID_1_TOTAL_DATA_VIEW_FILE': 'q100viz/settings/total_data_view_grid_1.csv',
    'GRID_2_TOTAL_DATA_VIEW_FILE': 'q100viz/settings/total_data_view_grid_2.csv',

    'GRID_2_X1' : 50,
    'GRID_2_X2' : 100,
    'GRID_2_Y1' : 0,
    'GRID_2_Y2' : 86.27,

    'GRID_1_X1' : 0,
    'GRID_1_X2' : 50,
    'GRID_1_Y1' : 0,
    'GRID_1_Y2' : 86.27,

    # interaction tuning
    'buildings_selection_mode': 'rotation' # select 'all' intersected buildings or choose by 'rotation'

}

COMMUNICATION_RELEVANT_KEYS = ['address', 'avg_spec_heat_consumption', 'avg_spec_power_consumption', 'cluster_size', 'emissions_graphs', 'energy_prices_graphs', 'CO2', 'connection_to_heat_grid', 'connection_to_heat_grid_prior', 'refurbished', 'refurbished_prior', 'environmental_engagement', 'environmental_engagement_prior', 'energy_source', 'cell']

def main():
    simulation = SimulationMode()
    simulation.activate()

class SimulationMode:
    def __init__(self):

        self.cwd = os.getcwd()  # hold current working directory to return to later

        # simulation setup
        self.headless_folder = config['GAMA_HEADLESS_FOLDER']
        self.script = self.headless_folder + 'gama-headless.sh'
        self.current_output_folder = ''  # will be set in activate()
        self.xml_path = ''               # will be set in activate()
        self.final_step = None           # will be set in activate()
        self.output_folders = []         # list of output folders of all game rounds
        self.using_timestamp = True

        self.matplotlib_neighborhood_images = {}

        self.xml = None

    def activate(self):

        self.final_step = config['SIMULATION_NUM_STEPS']
        self.model_file = os.path.normpath(
            os.path.join(self.cwd, config['GAMA_MODEL_FILE']))

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
        scenario_data = {
            'A': pandas.read_csv(
                '../../data/scenario_A.csv').set_index('name'),
            'B': pandas.read_csv(
                '../../data/scenario_B.csv').set_index('name'),
            'C': pandas.read_csv(
                '../../data/scenario_C.csv').set_index('name'),
            'D': pandas.read_csv(
                '../../data/scenario_D.csv').set_index('name'),
            'Ref': pandas.read_csv(
                '../../data/scenario_Ref.csv').set_index('name')
        }

        # pick a scenario:
        active_scenario_handle = 'Ref'

        # provide parameters:
        params = pandas.DataFrame(columns=['name', 'type', 'value', 'var'])
        params.loc[len(params)] = ['timestamp', 'STRING',
                                   self.timestamp, 'timestamp']

        # values to be used in trend model:
        params.loc[len(params)] = ['Alpha scenario', 'STRING',
                                   scenario_data[active_scenario_handle].loc['alpha_scenario', 'value'], 'alpha_scenario']
        params.loc[len(params)] = ['Carbon price scenario', 'STRING',
                                   scenario_data[active_scenario_handle].loc['carbon_price_scenario', 'value'], 'carbon_price_scenario']
        params.loc[len(params)] = ['Energy prices scenario', 'STRING',
                                   scenario_data[active_scenario_handle].loc['energy_price_scenario', 'value'], 'energy_price_scenario']
        params.loc[len(params)] = ['Q100 OpEx prices scenario', 'STRING',
                                   scenario_data[active_scenario_handle].loc['q100_price_opex_scenario', 'value'], 'q100_price_opex_scenario']
        params.loc[len(params)] = ['Q100 CapEx prices scenario', 'STRING',
                                   scenario_data[active_scenario_handle].loc['q100_price_capex_scenario', 'value'], 'q100_price_capex_scenario']
        params.loc[len(params)] = ['Q100 Emissions scenario', 'STRING',
                                   scenario_data[active_scenario_handle].loc['q100_emissions_scenario', 'value'], 'q100_emissions_scenario']
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
            self.timestamp)) if self.using_timestamp else '../../data/output/buildings_clusters_{0}.csv'.format(str(self.timestamp))

        print(clusters_outname)

        if not os.path.isdir(self.current_output_folder):
            os.makedirs(self.current_output_folder)

        # debug: select 5 random buildings:
        random_bd = buildings_df.sample(n=5)
        random_bd['selected'] = True
        random_bd['group'] = [random.randint(0, 3) for x in random_bd.values]
        random_bd['connection_to_heat_grid'] = True
        buildings_df.update(random_bd)

        # put these into user groups:
        buildings_groups_list = [
            buildings_df[buildings_df['group'] == 0][COMMUNICATION_RELEVANT_KEYS],
            buildings_df[buildings_df['group'] == 1][COMMUNICATION_RELEVANT_KEYS],
            buildings_df[buildings_df['group'] == 2][COMMUNICATION_RELEVANT_KEYS],
            buildings_df[buildings_df['group'] == 3][COMMUNICATION_RELEVANT_KEYS]]


        selected_buildings = buildings_df[buildings_df.selected]
        selected_buildings[['spec_heat_consumption', 'spec_power_consumption', 'energy_source', 'electricity_supplier',
            'connection_to_heat_grid', 'refurbished', 'environmental_engagement']].to_csv(clusters_outname)

        # start simulation
        self.make_xml(params, outputs, self.xml_path,
                      self.final_step, None, 'agent_decision_making')
        self.run_script(self.xml_path)

    ########################### script: prepare #######################
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

        os.chdir(self.cwd)  # return to previous cwd

if __name__ == '__main__':
    main()