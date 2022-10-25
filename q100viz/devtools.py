######################## dev tools ##########################
import random
import pandas

def print_verbose(message, VERBOSE_MODE, log):
    if VERBOSE_MODE:
        print(message)
        if log: log += ("\n" + message)

def select_random_buildings_for_simulation(buildings_df, num_buildings=1, max_buildings_group=4, connection_to_heat_grid=False, refurbished=False, save_energy=False):
        '''pick random n buildings, activate for simulation and update buildings list'''

        # get n buildings from buildings dataframe:
        df = buildings_df.sample(n=num_buildings)
        for i, idx in enumerate(df.index):
                df.at[idx, 'group'] = i % max_buildings_group  # values from 0 to 4, group determines allocation to quarterSection on infoscreen
        df['selected'] = True  # only selected buildings are exported for simulation
        # optional decision adjustments:
        df['connection_to_heat_grid'] = connection_to_heat_grid
        df['refurbished'] = refurbished
        df['save_energy'] = save_energy

        buildings_df.update(df)

def select_buildings_for_simulation(buildings_df, list_of_buildings_indices, max_buildings_group=4, connection_to_heat_grid=False, refurbished=False, save_energy=False):
        '''update buildings list with specific selected buildings adjusted for simulation'''

        # get n buildings from buildings dataframe:
        df = buildings_df.loc[list_of_buildings_indices]
        for i, idx in enumerate(df.index):
                df.at[idx, 'group'] = i % max_buildings_group  # values from 0 to 4, group determines allocation to quarterSection on infoscreen
        df['selected'] = True  # only selected buildings are exported for simulation
        # optional decision adjustments:
        df['connection_to_heat_grid'] = connection_to_heat_grid
        df['refurbished'] = refurbished
        df['save_energy'] = save_energy

        buildings_df.update(df)

def print_full_df(df):
    with pandas.option_context('display.max_rows', None,
                               'display.max_columns', None,
                               'display.precision', 3,
                               ):
        print(df)
