import geopandas
import pandas
import random

crs = "EPSG:3857"
######################## dev tools ##########################
def print_full_df(df):
    with pandas.option_context('display.max_rows', None,
                           'display.max_columns', None,
                           'display.precision', 3,
                           ):
        print(df)

def read_shapefile(file, layer=None, columns=None):
    df = geopandas.read_file(file, layer=layer).to_crs(crs=crs)
    if columns:
        df = df.astype(columns)
        return df.loc[:, ['geometry', *columns.keys()]]
    return df

########################## buildings ########################
def make_clusters(group_selection):
    '''make groups of the selected buildings. group by standard deviation of energy consumption'''
    cluster_list = []
    for idx in range(len(group_selection.index)):
        interval = 0.5  # standard deviation
        cluster = pandas.DataFrame()
        while len(cluster) < 2:  # make sure no building is alone
            cluster = buildings_df.loc[(
                    (buildings_df['energy_source'] == buildings_df.loc[
                        buildings_df.index[idx], 'energy_source'])
                    &
                    (buildings_df['spec_heat_consumption'] >= buildings_df.loc[buildings_df.index[idx],
                    'spec_heat_consumption'] - buildings_df['spec_heat_consumption'].std() * interval)
                    &
                    (buildings_df['spec_heat_consumption'] <= buildings_df.loc[buildings_df.index[idx],
                    'spec_heat_consumption'] + buildings_df['spec_heat_consumption'].std() * interval)
                    &
                    (buildings_df['spec_power_consumption'] >= buildings_df.loc[buildings_df.index[idx],
                    'spec_power_consumption'] - buildings_df['spec_power_consumption'].std() * interval)
                    &
                    (buildings_df['spec_power_consumption'] <= buildings_df.loc[buildings_df.index[idx],
                    'spec_power_consumption'] + buildings_df['spec_power_consumption'].std() * interval)
                )]
            interval += 0.1  # increase range, try again if necessary

        cluster_list.append(cluster)
        print(
            "building {0} is in a group of to {1} buildings with similar specs:".format(group_selection.index[idx], len(cluster)))
        # print_verbose(cluster[['spec_heat_consumption', 'spec_power_consumption']].describe())

    return cluster_list

##################### Load data #####################
buildings_df = pandas.DataFrame()
buildings_df['energy_source'] = None

# buildings_df:
buildings_df = read_shapefile(
    "../../data/GIS/Shapefiles/bestandsgebaeude_export.shp", columns={
        'Kataster_C': 'string',
        'Kataster_S': 'string',
        'Kataster_H': 'string',
        'Kataster13': 'float',
        'Kataster15': 'float',
        'Kataster_E': 'string'}).set_index('Kataster_C')

buildings_df.index.names = ['id']

buildings_df['address'] = buildings_df['Kataster_S'] + ' ' + buildings_df['Kataster_H']
buildings_df = buildings_df.drop('Kataster_S', 1)
buildings_df = buildings_df.drop('Kataster_H', 1)
buildings_df = buildings_df.rename(columns = {'Kataster13': 'spec_heat_consumption', 'Kataster15': 'spec_power_consumption', 'Kataster_E': 'energy_source'})

# adjust data
buildings_df['spec_heat_consumption'] = buildings_df['spec_heat_consumption'].fillna(0).to_numpy()
buildings_df['avg_spec_heat_consumption'] = 0
buildings_df['spec_power_consumption'] = buildings_df['spec_power_consumption'].fillna(0).to_numpy()
buildings_df['avg_spec_power_consumption'] = 0
buildings_df['cluster_size'] = 0

buildings_cluster = make_clusters(buildings_df)
# update building with average data:
for j in range(len(buildings_df)):
    buildings_df.at[buildings_df.index[j], 'avg_spec_heat_consumption'] = buildings_cluster[j]['spec_heat_consumption'].mean()
    buildings_df.at[buildings_df.index[j], 'avg_spec_power_consumption'] = buildings_cluster[j]['spec_power_consumption'].mean()
    buildings_df.at[buildings_df.index[j], 'cluster_size'] = int(len(buildings_cluster[j]))

buildings_df['emissions_graphs'] = ''
buildings_df['energy_prices_graphs'] = ''

# generic data
buildings_df['CO2'] = (buildings_df['spec_heat_consumption'] + buildings_df['spec_power_consumption']) / 20000

electricity_supply_types = ['green', 'gray', 'mix']
buildings_df['electricity_supplier'] = [electricity_supply_types[random.randint(0,2)] for row in buildings_df.values]

buildings_df['connection_to_heat_grid'] = buildings_df['energy_source'].isna().to_numpy()
buildings_df['connection_to_heat_grid_prior'] = buildings_df['connection_to_heat_grid']

buildings_df['refurbished'] = buildings_df['connection_to_heat_grid']
buildings_df['refurbished_prior'] = buildings_df['refurbished']

buildings_df['environmental_engagement'] = [True if random.random() > 0.5 else False for row in buildings_df.values]
buildings_df['environmental_engagement_prior'] = buildings_df['environmental_engagement']

# buildings interaction
buildings_df['cell'] = ""
buildings_df['selected'] = False
buildings_df['group'] = -1
