from q100viz.interaction.calibration_mode import CalibrationMode
from q100viz.interaction.edit_mode import EditMode
from q100viz.interaction.tui_mode import TuiMode, Slider
from q100viz.interaction.simulation_mode import SimulationMode

'''This module keeps variables shared among other modules.'''

# graphics
viewport = None
gis = None
basemap = None
grid_1 = None
grid_2 = None
buildings = None
environment = {'foerderung': 0}
verbose = True
slider_handles = ['year', 'foerderung', ' CO2-Preis',
                    'CO2-emissions', 'versorgung', 'investment', 'anschluss']

# interaction
seconds_elapsed = 0
ticks_elapsed = 0

handlers = {
    'calibrate': CalibrationMode(),
    'edit': EditMode(),
    'tui': TuiMode(),
    'simulation': SimulationMode()
}
active_handler = handlers['tui']

# global functions:
def print_verbose(message):
    if verbose:
        print(message)