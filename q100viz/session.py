'''This module keeps variables shared among other modules.'''

import pandas as pd
import pygame

from q100viz.settings.config import config
import q100viz.api as api
from q100viz.interaction.calibration_mode import CalibrationMode
from q100viz.interaction.questionnaire_mode import Questionnaire_Mode
from q100viz.interaction.input_scenarios_mode import Input_Scenarios
from q100viz.interaction.input_households_mode import Input_Households
from q100viz.interaction.simulation_mode import SimulationMode
from q100viz.interaction.dataview_individual_mode import DataViewIndividual_Mode
from q100viz.interaction.dataview_total_mode import DataViewTotal_Mode
import q100viz.keystone as keystone

log = ""
DEBUG_MODE = False
VERBOSE_MODE = True

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
    print('loading src_points:' , viewport.src_points)
    print('loading dst_points:' , viewport.dst_points)
except Exception:
    print("Failed to open keystone file")
    viewport.src_points = [[0, 0], [0, 100], [100, 100], [100, 0]]
    viewport.dst_points = [[0, 0], [0, canvas_size[1]], [canvas_size[0], canvas_size[1]], [canvas_size[0], 0]]
viewport.calculate()

##################### global variables: #####################
gis = None
basemap = None
grid_1 = None
grid_2 = None
buildings = None
buildings_groups = None

environment = {'mode': 'input_scenarios'}

num_of_questions = 5  # TODO: this equals length of csv
environment['active_scenario'] = 'Ref'

input_households_grid_1 = pd.read_csv(config['GRID_1_SETUP_FILE'])
input_households_grid_2 = pd.read_csv(config['GRID_2_SETUP_FILE'])
input_scenarios_grid_1 = pd.read_csv(config['GRID_1_INPUT_SCENARIOS_FILE'])
input_scenarios_grid_2 = pd.read_csv(config['GRID_2_INPUT_SCENARIOS_FILE'])
data_view_grid_1 = pd.read_csv(config['GRID_1_DATA_VIEW_FILE'])
data_view_grid_2 = pd.read_csv(config['GRID_2_DATA_VIEW_FILE'])

# list of possible handles
input_scenarios_variables = ['CO2-prize', 'renovation_cost']
mode_selector_handles = ['start_input_scenarios', 'start_input_households', 'start_simulation']
communication_relevant_keys = ['address', 'CO2', 'connection_to_heat_grid', 'refurbished', 'environmental_engagement', 'cell']

# interaction
seconds_elapsed = 0
ticks_elapsed = 0

num_of_rounds = 4  # max num of rounds; will repeat after this
num_of_users = 4 # num of valid users # TODO: combine with num of valid tags!
iteration_round = 0   # num of q-scope iterations during this workshops
gama_iteration_images = ['' for n in range(num_of_rounds)]
emissions_data_paths = ['' for n in range(num_of_rounds)]

handlers = {
    'calibrate': CalibrationMode(),
    'questionnaire': Questionnaire_Mode(),
    'input_scenarios': Input_Scenarios(),
    'input_households': Input_Households(),
    'simulation': SimulationMode(),
    'data_view_individual': DataViewIndividual_Mode(),
    'data_view_total' : DataViewTotal_Mode()
}
active_handler = handlers['input_scenarios']
flag_export_canvas = False

# global functions:
def print_verbose(message):
    if VERBOSE_MODE:
        print(message)

def print_full_df(df):
    with pd.option_context('display.max_rows', None,
                        'display.max_columns', None,
                        'display.precision', 3,
                        ):
        print(df)