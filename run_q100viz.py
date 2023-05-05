import argparse

from q100viz.settings.config import config
import q100viz.session as session

from q100viz.frontend import Frontend

################################ STARTUP ##############################
##################### parse command line arguments ####################
parser = argparse.ArgumentParser()
parser.add_argument('--select_random',
                    help="select n random buildings", type=int, default=0)
parser.add_argument('--verbose', '-v',
                    help="start in verbose mode", action='store_true')
parser.add_argument(
    '--simulate_until', help="max_year of simulation", type=int, default=config['SIMULATION_FORCE_END_YEAR'])
parser.add_argument(
    '--connect', '-c', help="specify year of connection for selected buildings", type=int, default=0)
parser.add_argument('--refurbish', '-r',
                    help="refurbish all selected buildings", action='store_true')
parser.add_argument('--save_energy', '-e',
                    help="set all selected buildings to save_energy", action='store_true')
parser.add_argument('--start_at', help="start at specific game mode",
                    type=str, default=session.environment['mode'])
parser.add_argument(
    '--main_window', help="runs program in main window", action='store_true')
parser.add_argument('--research_model',
                    help="use research model instead of q-Scope-interaction model", action='store_true')

args = parser.parse_args()

########################### debug setup ###############################
session.debug_num_of_random_buildings = args.select_random
config['SIMULATION_FORCE_END_YEAR'] = args.simulate_until
session.debug_connection_date = args.connect        # force buildings to opt in 'connection_to_heat_grid'
session.debug_force_refurbished = args.refurbish    # force buildings to opt in 'refurbish'
session.debug_force_save_energy = args.save_energy  # force buildings to opt in for 'save_energy'
session.active_mode = session.string_to_mode(args.start_at)  # force start at this mode
session.VERBOSE_MODE = args.verbose  # define verbose level
config['GAMA_MODEL_FILE'] = '../q100_abm/q100/models/qscope_ABM.gaml' if args.research_model else config['GAMA_MODEL_FILE']

# compose startup information:
str_num_connections = '\n- random {0} buildings will be selected]'.format(session.debug_num_of_random_buildings) if session.debug_num_of_random_buildings > 0 else ''
str_date_of_connections = '\n- connect selected buildings in year {0}'.format(
    session.debug_connection_date) if session.debug_connection_date > 0 else ''
str_sim_until = '\n- simulate until year {0}'.format(
    config['SIMULATION_FORCE_END_YEAR']) if config['SIMULATION_FORCE_END_YEAR'] != 0 else 'simulation will run as specified via ../data/includes/csv-data_technical/initial_variables.csv'
str_sim_model_file = '\n- using simulation model file {0}.'.format(
    str(config['GAMA_MODEL_FILE'])
)
# print startup information:
print('\n', '#' * 28, " RUNTIME SETUP ", '#' * 28)
print(
    str_num_connections,
    str_date_of_connections,
    str_sim_until,
    str_sim_model_file)

print('\n', '#' * 72, '\n')

############################# game loop ###############################
frontend = Frontend(args.main_window)

while True:
    frontend.run()