'''This module keeps variables shared among other modules.'''

import pandas as pd
import csv

from config import config
from q100viz.interaction.calibration_mode import CalibrationMode
from q100viz.interaction.input_mode import InputMode, Input_Environment
from q100viz.interaction.simulation_mode import SimulationMode
from q100viz.interaction.questionnaire_mode import Questionnaire_Mode

log = ""

# graphics
viewport = None
gis = None
basemap = None
grid_1 = None
grid_2 = None
buildings = None
verbose = True

environment = {'mode': 'input_environment'}

with open(config['QUESTIONS_FILE'], newline='') as f:
    environment['num_questions'] = len(list(csv.reader(f)))

input_households_grid_1 = pd.read_csv(config['GRID_1_SETUP_FILE'])
input_households_grid_2 = pd.read_csv(config['GRID_2_SETUP_FILE'])
input_environment_grid_1 = pd.read_csv(config['GRID_1_INPUT_ENVIRONMENT_FILE'])
input_environment_grid_2 = pd.read_csv(config['GRID_2_INPUT_ENVIRONMENT_FILE'])

# list of possible handles
input_environment_variables = ['CO2-prize', 'renovation_cost']
mode_selector_handles = ['start_input_environment', 'start_input_households']

# interaction
seconds_elapsed = 0
ticks_elapsed = 0

handlers = {
    'calibrate': CalibrationMode(),
    # 'edit': EditMode(),
    'input_environment': Input_Environment(),
    'input_households': InputMode(),
    'simulation': SimulationMode(),
    'questionnaire': Questionnaire_Mode()
}
active_handler = handlers['questionnaire']
flag_export_canvas = False

# global functions:
def print_verbose(message):
    if verbose:
        print(message)