'''This module keeps variables shared among other modules.'''

# graphics
viewport = None
gis = None
basemap = None
grid_1 = None
grid_2 = None
buildings = None
environment = {'foerderung': 0}
verbose = False
slider_handles = ['year', 'foerderung', ' CO2-Preis',
                    'CO2-emissions', 'versorgung', 'investment', 'anschluss']

# interaction
seconds_elapsed = 0
ticks_elapsed = 0

# global functions:
def print_verbose(message):
    if verbose:
        print(message)