'''This module keeps variables shared among other modules.'''

import pandas as pd

from q100viz.interaction.calibration_mode import CalibrationMode
# from q100viz.interaction.edit_mode import EditMode
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

environment['questions'] = [  # TODO: externalize this to yet another csv

        "Die globale Erderwärmung wird durch von Menschen produzierte Emissionen verstärkt.",
        "Der Schutz der Umwelt ist ein Mittel zur Stärkung des Wirtschaftswachstums in Deutschland.",
        "Ich glaube, dass wir jedes Mal, wenn wir Kohle, Öl oder Gas verwenden, zum Klimawandel beitragen.",
        "Ich würde meinen Energieverbrauch reduzieren, wenn mein Haushalt mehr Energie verbraucht als ähnliche Haushalte.",
        "Wenn ein erneuerbarer Energietarif bei einem anderen Energieversorger verfügbar wäre, würde ich meinen Anbieter wechseln."
]
environment['question'] = environment['questions'][0]

input_households_grid_1 = pd.read_csv('/home/dunland/github/qScope/data/grid_1_setup.csv')
input_households_grid_2 = pd.read_csv('/home/dunland/github/qScope/data/grid_2_setup.csv')
input_environment_grid_1 = pd.read_csv('/home/dunland/github/qScope/data/input_environment_grid_1.csv')
input_environment_grid_2 = pd.read_csv('/home/dunland/github/qScope/data/input_environment_grid_2.csv')

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