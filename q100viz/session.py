'''This module keeps variables shared among other modules.'''

import pandas as pd
import pygame
import json

from q100viz.settings.config import config
import q100viz.api as api
import q100viz.gis as gis
import q100viz.grid as grid
from q100viz.interaction.calibration_mode import CalibrationMode
from q100viz.interaction.buildings_interaction import Buildings_Interaction
from q100viz.interaction.simulation_mode import SimulationMode
from q100viz.interaction.individual_data_view import DataViewIndividual_Mode
from q100viz.interaction.total_data_view import DataViewTotal_Mode
import q100viz.keystone as keystone
import q100viz.buildings
from q100viz.devtools import devtools as devtools

#----------------------- dev and debug variables ----------------------
debug_num_of_random_buildings = 0
debug_connection_date = 0
debug_refurb_year = 0
debug_force_save_energy = False

# ---------------------- infoscreen communication ---------------------
io = 'http://localhost:' + str(config['UDP_SERVER_PORT'])  # Socket.io
api = api.API(io)

#------------------------------ graphics ------------------------------

# create the main surface, projected to corner points
# the viewport's coordinates are between 0 and 100 on each axis
viewport = keystone.Surface(config['CANVAS_SIZE'], pygame.SRCALPHA)
try:
    viewport.load(config['SAVED_KEYSTONE_FILE'])
    devtools.print_verbose('...viewport points loaded from keystone file.')
except Exception:
    devtools.print_verbose("Failed to open keystone file")
    viewport.src_points = [[0, 0], [0, 100], [100, 100], [100, 0]]
    viewport.dst_points = [[0, 0], [0, config['CANVAS_SIZE'][1]], [
        config['CANVAS_SIZE'][0], config['CANVAS_SIZE'][1]], [config['CANVAS_SIZE'][0], 0]]
viewport.calculate()

show_polygons = False
show_basemap = False

#------------------------------ interaction ---------------------------
num_of_rounds = config['NUM_OF_ROUNDS']  # max num of rounds; will repeat after this
num_of_users = config['NUM_OF_USERS']  # num of valid users # TODO: combine with num of valid tags!
user_colors = [
    (0, 117, 180),   # Quarree-blue  #0075b4
    (253, 193, 19),  # Quarree-yellow  #fdc113
    (182, 0, 182),   # purple  #b600b6
    (0, 168, 78),    # Quarree-dark-green  #00a84e
    (186, 212, 50),  # Quarree-light-green
    (155, 155, 155)
]

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

gama_iteration_images = ['' for n in range(num_of_rounds)]
emissions_data_paths = ['' for n in range(num_of_rounds)]

#-------------------------- global variables: -------------------------
buildings = q100viz.buildings.Buildings()

scenario_selected_buildings = pd.DataFrame()

# list of possible handles
MODE_SELECTOR_HANDLES = ['start_individual_data_view', 'start_total_data_view', 'start_buildings_interaction', 'start_simulation']
# columns exported from buildings.df for communication with GAMA and Infoscreen. ATTENTION: When this is changed, make sure to change it in GAMA and infoscreen likewise!
COMMUNICATION_RELEVANT_KEYS = ['address', 'spec_heat_consumption', 'spec_power_consumption', 'type', 'cluster_size', 'emissions_graphs', 'energy_prices_graphs', 'connection_to_heat_grid', 'connection_to_heat_grid_prior', 'refurbished', 'refurbished_prior', 'save_energy', 'save_energy_prior', 'energy_source', 'cell']
VALID_DECISION_HANDLES = ['connection_to_heat_grid', 'refurbished', 'save_energy']

# environment (used for communication with infoscreen)
environment = {
    'mode': 'buildings_interaction',
    'scenario_energy_prices' : 2018,
    'scenario_num_connections' : 0,  # how many more buildings to connect?
    'current_iteration_round' : 0, # num of q-scope iterations during this workshop
    'active_user_focus_data' : -1  # determines which user data to focus in individual data view
    }

# scenario data:
environment['active_scenario_handle'] = 'A'
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

# ---------------------------- simulation -----------------------------
min_connection_year = config['SIMULATION_FORCE_START_YEAR']
min_refurb_year = config['SIMULATION_FORCE_START_YEAR']

############################## INITIALIZATION #########################
#--------------------------------- gis --------------------------------
# Initialize geographic viewport and basemap
_gis = gis.GIS(
    config['CANVAS_SIZE'],
    # northeast          northwest           southwest           southeast
    [[1013631, 7207409], [1012961, 7207198], [1013359, 7205932], [1014029, 7206143]],
    viewport)

basemap = gis.Basemap(
    config['CANVAS_SIZE'], config['BASEMAP_FILE'],
    # northwest          southwest           southeast           northeast
    [[1012695, 7207571], [1012695, 7205976], [1014205, 7205976], [1014205, 7207571]],
    _gis)
basemap.warp()

# ------------------------------ grid ---------------------------------
###### Initialize grid, projected onto the viewport #########
grid_settings = json.load(open(config['CSPY_SETTINGS_FILE']))  # TODO: seperate files for the two grids
nrows = grid_settings['nrows']
ncols = grid_settings['ncols']
grid_1 = grid.Grid(
    config['CANVAS_SIZE'], ncols, nrows, [
        [config['GRID_1_X1'], config['GRID_1_Y1']],
        [config['GRID_1_X1'], config['GRID_1_Y2']],
        [config['GRID_1_X2'], config['GRID_1_Y2']],
        [config['GRID_1_X2'], config['GRID_1_Y1']]],
        viewport, config['GRID_1_SETUP_FILE'],
        {'slider0' : [[0, 115], [0, 100], [50, 100], [50, 115]],
            'slider1' : [[50, 115], [50, 100], [100, 100], [100, 115]]},
        {'slider0' : (0, int(ncols/2)),
        'slider1' : (int(ncols/2), ncols)})
grid_2 = grid.Grid(
    config['CANVAS_SIZE'], ncols, nrows, [
        [config['GRID_2_X1'], config['GRID_2_Y1']],
        [config['GRID_2_X1'], config['GRID_2_Y2']],
        [config['GRID_2_X2'], config['GRID_2_Y2']],
        [config['GRID_2_X2'], config['GRID_2_Y1']]],
        viewport, config['GRID_2_SETUP_FILE'],
        {'slider2' : [[0, 115], [0, 100], [50, 100], [50, 115]],
         'slider3' : [[50, 115], [50, 100], [100, 100], [100, 115]]},
        {'slider2' : (0, int(ncols/2)),
        'slider3' : (int(ncols/2), ncols)})

slider0 = grid_1.sliders['slider0']
slider1 = grid_1.sliders['slider1']
slider2 = grid_2.sliders['slider2']
slider3 = grid_2.sliders['slider3']

# --------------------------- init buildings: -------------------------
buildings.load_data()

# ----------------------- mode-specific grid setup: -------------------
buildings_interaction_grid_1 = pd.read_csv(config['GRID_1_SETUP_FILE'])
buildings_interaction_grid_2 = pd.read_csv(config['GRID_2_SETUP_FILE'])
input_scenarios_grid_1 = pd.read_csv(config['GRID_1_INPUT_SCENARIOS_FILE'])
input_scenarios_grid_2 = pd.read_csv(config['GRID_2_INPUT_SCENARIOS_FILE'])
individual_data_view_grid_1 = pd.read_csv(config['GRID_1_INDIVIDUAL_DATA_VIEW_FILE'])
individual_data_view_grid_2 = pd.read_csv(config['GRID_2_INDIVIDUAL_DATA_VIEW_FILE'])
total_data_view_grid_1 = pd.read_csv(config['GRID_1_TOTAL_DATA_VIEW_FILE'])
total_data_view_grid_2 = pd.read_csv(config['GRID_2_TOTAL_DATA_VIEW_FILE'])

# -------------------------------- modes ------------------------------
previous_mode = None
pending_mode = None  # next mode to run after countdown

calibration = CalibrationMode()
buildings_interaction = Buildings_Interaction()
simulation = SimulationMode()
individual_data_view = DataViewIndividual_Mode()
total_data_view = DataViewTotal_Mode()

modes = [buildings_interaction, simulation, individual_data_view, total_data_view]

################################# FUNCTIONS ###########################
def string_to_mode(input_string):
    if input_string == 'calibrate':
        return calibration
    elif input_string == 'buildings_interaction':
        return buildings_interaction
    elif input_string == 'simulation':
        return simulation
    elif input_string == 'individual_data_view':
        return individual_data_view
    elif input_string == 'total_data_view':
        return total_data_view
    else:
        print(input_string, "is not a defined game mode. starting at buildings_interaction..")
        return buildings_interaction

flag_export_canvas = False
active_mode = string_to_mode(environment['mode'])

def iterate_grids():

    return [(x, y, cell, grid) for grid in [grid_1, grid_2] for y, row in enumerate(grid.grid) for x, cell in enumerate(row)]

frontend = None  # will be set in run_q100viz.py