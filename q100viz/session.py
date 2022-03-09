'''This module keeps variables shared among other modules.'''

from q100viz.interaction.calibration_mode import CalibrationMode
# from q100viz.interaction.edit_mode import EditMode
from q100viz.interaction.input_mode import InputMode
from q100viz.interaction.simulation_mode import SimulationMode
from q100viz.interaction.questionnaire_mode import Questionnaire_Mode


# graphics
viewport = None
gis = None
basemap = None
grid_1 = None
grid_2 = None
buildings = None
verbose = True
slider_handles = ['year', 'foerderung', 'CO2-Preis',
                    'CO2-emissions', 'versorgung', 'investment', 'anschluss', 'connection_speed']
environment = dict.fromkeys(slider_handles, 0)
environment['mode'] = 'input'

# interaction
seconds_elapsed = 0
ticks_elapsed = 0

handlers = {
    'calibrate': CalibrationMode(),
    # 'edit': EditMode(),
    'input': InputMode(),
    'simulation': SimulationMode(),
    'questionnaire': Questionnaire_Mode()
}
active_handler = handlers['questionnaire']
flag_export_canvas = False

# global functions:
def print_verbose(message):
    if verbose:
        print(message)