'''This module keeps variables shared among other modules.'''

import pandas as pd
import pygame

from q100viz.settings.config import config
import q100viz.api as api
from q100viz.interaction.calibration_mode import CalibrationMode
from q100viz.interaction.questionnaire_mode import Questionnaire_Mode
# from q100viz.interaction.input_scenarios_mode import Input_Scenarios
from q100viz.interaction.buildings_interaction import Buildings_Interaction
from q100viz.interaction.simulation_mode import SimulationMode
from q100viz.interaction.dataview_individual_mode import DataViewIndividual_Mode
from q100viz.interaction.dataview_total_mode import DataViewTotal_Mode
import q100viz.keystone as keystone
import q100viz.buildings

################### dev and debug variables #################
log = ""
TEST_MODE = ""
VERBOSE_MODE = False

debug_num_of_random_buildings = 0
debug_force_connect = False

# ################# infoscreen communication ################
io = 'http://localhost:8081'  # Socket.io
api = api.API(io)

########################## graphics #########################
quarree_colors_8bit = [   # corporate design of QUARREE100
    (0, 117, 180),   # Quarree-blue
    (253, 193, 19),  # Quarree-yellow
    (0, 168, 78),    # Quarree-dark-green
    (186, 212, 50),  # Quarree-light-green
    (103, 102, 104)  # Quarree-gray
]
quarree_colors_float = [   # corporate design of QUARREE100
    (0/255, 117/255, 180/255),   # Quarree-blue
    (253/255, 193/255, 19/255),  # Quarree-yellow
    (0/255, 168/255, 78/255),    # Quarree-dark-green
    (186/255, 212/255, 50/255),  # Quarree-light-green
    (103/255, 102/255, 104/255)  # Quarree-gray
]
canvas_size = 1920, 1080

# create the main surface, projected to corner points
# the viewport's coordinates are between 0 and 100 on each axis
viewport = keystone.Surface(canvas_size, pygame.SRCALPHA)
try:
    viewport.load(config['SAVED_KEYSTONE_FILE'])
    print('loading src_points:', viewport.src_points)
    print('loading dst_points:', viewport.dst_points)
except Exception:
    print("Failed to open keystone file")
    viewport.src_points = [[0, 0], [0, 100], [100, 100], [100, 0]]
    viewport.dst_points = [[0, 0], [0, canvas_size[1]], [
        canvas_size[0], canvas_size[1]], [canvas_size[0], 0]]
viewport.calculate()

####################### interaction #########################
num_of_rounds = 4  # max num of rounds; will repeat after this
num_of_users = 4  # num of valid users # TODO: combine with num of valid tags!
gama_iteration_images = ['' for n in range(num_of_rounds)]
emissions_data_paths = ['' for n in range(num_of_rounds)]
##################### global variables: #####################
gis = None
basemap = None
grid_1 = None
grid_2 = None
buildings = q100viz.buildings.Buildings()
buildings_groups_list = [None for n in range(num_of_users)]
scenario_selected_buildings = pd.DataFrame()
seconds_elapsed = 0
ticks_elapsed = 0

environment = {
    'mode': 'buildings_interaction',
    'scenario_energy_prices' : 2018,
    'scenario_num_connections' : 0,  # how many more buildings to connect?
    'iteration_round' : 0 # num of q-scope iterations during this workshops
    }

num_of_questions = 5  # TODO: this equals length of csv
environment['active_scenario_handle'] = 'Ref'
scenario_data = {
    'A': pd.read_csv(
        '../data/scenario_A.csv').set_index('name'),
    'B': pd.read_csv(
        '../data/scenario_B.csv').set_index('name'),
    'C': pd.read_csv(
        '../data/scenario_C.csv').set_index('name'),
    'D': pd.read_csv(
        '../data/scenario_D.csv').set_index('name'),
    'Ref': pd.read_csv(
        '../data/scenario_Ref.csv').set_index('name')
}

scenario_titles = {
    identifier : pd.read_csv('../data/scenario_titles.csv').set_index('scenario').at[identifier, 'name'] for identifier in scenario_data.keys()
}

buildings_interaction_grid_1 = pd.read_csv(config['GRID_1_SETUP_FILE'])
buildings_interaction_grid_2 = pd.read_csv(config['GRID_2_SETUP_FILE'])
input_scenarios_grid_1 = pd.read_csv(config['GRID_1_INPUT_SCENARIOS_FILE'])
input_scenarios_grid_2 = pd.read_csv(config['GRID_2_INPUT_SCENARIOS_FILE'])
individual_data_view_grid_1 = pd.read_csv(config['GRID_1_INDIVIDUAL_DATA_VIEW_FILE'])
individual_data_view_grid_2 = pd.read_csv(config['GRID_2_INDIVIDUAL_DATA_VIEW_FILE'])
total_data_view_grid_1 = pd.read_csv(config['GRID_1_TOTAL_DATA_VIEW_FILE'])
total_data_view_grid_2 = pd.read_csv(config['GRID_2_TOTAL_DATA_VIEW_FILE'])

# list of possible handles
mode_selector_handles = ['start_individual_data_view', 'start_total_data_view'
                         'start_buildings_interaction', 'start_simulation']
COMMUNICATION_RELEVANT_KEYS = ['address', 'avg_spec_heat_consumption', 'avg_spec_power_consumption', 'cluster_size', 'emissions_graphs', 'energy_prices_graphs', 'CO2', 'connection_to_heat_grid', 'connection_to_heat_grid_prior', 'refurbished', 'refurbished_prior', 'environmental_engagement', 'environmental_engagement_prior', 'energy_source', 'cell']
VALID_GRID_HANDLES = ['connection_to_heat_grid', 'electricity_supplier', 'refurbished', 'environmental_engagement', 'game_stage', 'num_connections', 'scenario_energy_prices']

handlers = {
    'calibrate': CalibrationMode(),
    'questionnaire': Questionnaire_Mode(),
    # 'input_scenarios': Input_Scenarios(),
    'buildings_interaction': Buildings_Interaction(),
    'simulation': SimulationMode(),
    'individual_data_view': DataViewIndividual_Mode(),
    'total_data_view': DataViewTotal_Mode()
}
active_handler = handlers[environment['mode']]
flag_export_canvas = False

######################## dev tools ##########################
def print_verbose(message):
    if VERBOSE_MODE:
        print(message)
