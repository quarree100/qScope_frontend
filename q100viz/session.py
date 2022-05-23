'''This module keeps variables shared among other modules.'''

import pandas as pd
import pygame

from config import config
from q100viz.interaction.calibration_mode import CalibrationMode
from q100viz.interaction.input_mode import Input_Households, Input_Environment
from q100viz.interaction.simulation_mode import SimulationMode
from q100viz.interaction.questionnaire_mode import Questionnaire_Mode
import q100viz.keystone as keystone

log = ""

# graphics
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

gis = None
basemap = None
grid_1 = None
grid_2 = None
buildings = None
verbose = True

environment = {'mode': 'input_environment'}

environment['questions'] = [  # TODO: externalize this to yet another csv

        "Die globale Erderwärmung wird durch von Menschen produzierte Emissionen verstärkt.",
        "Der Schutz der Umwelt ist ein Mittel zur Stärkung des Wirtschaftswachstums in Deutschland.",
        "Ich glaube, dass wir jedes Mal, wenn wir Kohle, Öl oder Gas verwenden, zum Klimawandel beitragen.",
        "Ich würde meinen Energieverbrauch reduzieren, wenn mein Haushalt mehr Energie verbraucht als ähnliche Haushalte.",
        "Wenn ein erneuerbarer Energietarif bei einem anderen Energieversorger verfügbar wäre, würde ich meinen Anbieter wechseln."
]
environment['question'] = environment['questions'][0]

input_households_grid_1 = pd.read_csv(config['GRID_1_SETUP_FILE'])
input_households_grid_2 = pd.read_csv(config['GRID_2_SETUP_FILE'])
input_environment_grid_1 = pd.read_csv(config['GRID_1_INPUT_ENVIRONMENT_FILE'])
input_environment_grid_2 = pd.read_csv(config['GRID_2_INPUT_ENVIRONMENT_FILE'])

# list of possible handles
input_environment_variables = ['CO2-prize', 'renovation_cost']
mode_selector_handles = ['start_input_environment', 'start_input_households', 'start_simulation']

# interaction
seconds_elapsed = 0
ticks_elapsed = 0

handlers = {
    'calibrate': CalibrationMode(),
    # 'edit': EditMode(),
    'input_environment': Input_Environment(),
    'input_households': Input_Households(),
    'simulation': SimulationMode(),
    'questionnaire': Questionnaire_Mode()
}
active_handler = handlers['questionnaire']
flag_export_canvas = False

# global functions:
def print_verbose(message):
    if verbose:
        print(message)