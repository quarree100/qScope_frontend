######################## dev tools ##########################
import random

def print_verbose(message, VERBOSE_MODE):
    if VERBOSE_MODE:
        print(message)

def select_random_buildings_for_simulation(buildings_df, num_buildings=1, max_buildings_group=3, connection_to_heat_grid=False, refurbished=False, save_energy=False):
        '''pick random n buildings, activate for simulation and update buildings list'''

        # get n buildings from buildings dataframe:
        df = buildings_df.sample(n=num_buildings)
        df['group'] = [random.randint(0, max_buildings_group) for row in df.values]  # group determines allocation to quarterSection on infoscreen
        df['selected'] = True  # only selected buildings are exported for simulation
        # optional decision adjustments:
        df['connection_to_heat_grid'] = connection_to_heat_grid
        df['refurbished'] = refurbished
        df['save_energy'] = save_energy

        buildings_df.update(df)

def select_buildings_for_simulation(buildings_df, list_of_buildings_indices, max_buildings_group=3, connection_to_heat_grid=False, refurbished=False, save_energy=False):
        '''update buildings list with specific selected buildings adjusted for simulation'''

        # get n buildings from buildings dataframe:
        df = buildings_df.loc[list_of_buildings_indices]
        df['group'] = [random.randint(0, max_buildings_group) for row in df.values]  # group determines allocation to quarterSection on infoscreen
        df['selected'] = True  # only selected buildings are exported for simulation
        # optional decision adjustments:
        df['connection_to_heat_grid'] = connection_to_heat_grid
        df['refurbished'] = refurbished
        df['save_energy'] = save_energy

        buildings_df.update(df)
        print(buildings_df[buildings_df['group'] >= 0]['group'])
