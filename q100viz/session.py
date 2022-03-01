'''This module keeps variables shared among other modules.'''

from q100viz.interaction.calibration_mode import CalibrationMode
# from q100viz.interaction.edit_mode import EditMode
from q100viz.interaction.input_mode import InputMode
from q100viz.interaction.simulation_mode import SimulationMode


# graphics
viewport = None
gis = None
basemap = None
grid_1 = None
grid_2 = None
buildings = None
verbose = True
slider_handles = ['year', 'foerderung', ' CO2-Preis',
                    'CO2-emissions', 'versorgung', 'investment', 'anschluss', 'connection_speed']
environment = dict.fromkeys(slider_handles, 0)

# interaction
seconds_elapsed = 0
ticks_elapsed = 0

handlers = {
    'calibrate': CalibrationMode(),
    # 'edit': EditMode(),
    'tui': InputMode(),
    'simulation': SimulationMode()
}
active_handler = handlers['tui']
flag_export_canvas = False

# global functions:
def print_verbose(message):
    if verbose:
        print(message)