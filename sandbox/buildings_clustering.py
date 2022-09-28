import geopandas
import pandas
import random
import json
import datetime

COMMUNICATION_RELEVANT_KEYS = [
    'address', 'CO2', 'connection_to_heat_grid', 'refurbished', 'environmental_engagement', 'cell']
crs = "EPSG:3857"

def read_shapefile(file, layer=None, columns=None):
    df = geopandas.read_file(file, layer=layer).to_crs(crs=crs)
    if columns:
        df = df.astype(columns)
        return df.loc[:, ['geometry', *columns.keys()]]
    return df


def send_message(self, msg):
    if msg != self.previous_message:
        print(datetime.datetime.now().strftime(" %H:%M:%S ") + "sending data:\n" + str(msg))
        try:
            self.io.emit('message', msg)
            self.previous_message = msg
        except Exception:
            pass

def export_json(df, outfile):
    """Export a dataframe to JSON file."""
    return pandas.DataFrame(df).to_json(
        outfile, orient='records', force_ascii=False, default_handler=str)

def make_clusters(group):
    '''make groups from one (!!) selected building. always only returns a cluster of the first building in group!'''
    cluster = buildings.loc[(
        (buildings['energy_source'] == group.loc[
            group.index[0], 'energy_source'])
        &
        (buildings['spec_heat_consumption'] >= buildings.loc[buildings.index[0], 'spec_heat_consumption'] - buildings['spec_heat_consumption'].std()/2)
        &
        (buildings['spec_heat_consumption'] <= buildings.loc[buildings.index[0], 'spec_heat_consumption'] + buildings['spec_heat_consumption'].std()/2)
        &
        (buildings['spec_power_consumption'] >= buildings.loc[buildings.index[0], 'spec_power_consumption'] - buildings['spec_power_consumption'].std()/2)
        &
        (buildings['spec_power_consumption'] <= buildings.loc[buildings.index[0], 'spec_power_consumption'] + buildings['spec_power_consumption'].std()/2)
        )]
    print("building {0} is linked to {1} other buildings with similar specs".format(group.index[0], len(cluster)))

    print("clustering end")
    return cluster

def make_groups(buildings):

    buildings

    buildings_groups = [
        buildings[buildings['group'] == 0][COMMUNICATION_RELEVANT_KEYS],
        buildings[buildings['group'] == 1][COMMUNICATION_RELEVANT_KEYS],
        buildings[buildings['group'] == 2][COMMUNICATION_RELEVANT_KEYS],
        buildings[buildings['group'] == 3][COMMUNICATION_RELEVANT_KEYS]]

    wrapper = ['' for i in range(4)]
    i = 0
    message = {}

    for group in buildings_groups:
            # aggregated data:
            connections_sum = group.groupby(
                by='cell')['connection_to_heat_grid' != False].sum()
            data = json.loads(export_json(
                connections_sum.rename('connections', inplace=True), None))

            print(connections_sum)
            print(data)

            group_data = {}
            if len(data) > 0:
                group_data = data[0]
                user_selected_buildings = json.loads(
                    export_json(group[COMMUNICATION_RELEVANT_KEYS], None))
                group_data['buildings'] = user_selected_buildings

                # get all buildings with similar stats
                buildings_cluster = make_clusters(group)
                # # get average building from this:
                # average_building = pandas.DataFrame()
                # for key in ['CO2', 'spec_heat_consumption', 'spec_power_consumption']:
                #     average_building[key] = [buildings_cluster[key].mean()]

                # group[0].update()
                # group_data['average_building'] = json.loads(export_json(average_building))

                # print(average_building)
                # make JSON serializable object from GeoDataFrame
                group_data['clusters'] = json.loads(
                    export_json(buildings_cluster))
                message['group_{0}'.format(str(i))] = group_data
            else:  # create empty elements for empty groups (infoscreen reset)
                message['group_{0}'.format(str(i))] = ['']

            wrapper = {
                'buildings_groups': message
            }

            i += 1

    print("grouping end")



##################### Load data #####################
buildings = pandas.DataFrame()
buildings['energy_source'] = None

# Bestand:
bestand = read_shapefile(
    "../data/GIS/Shapefiles/bestandsgebaeude_export.shp", columns={
        'Kataster_C': 'string',
        'Kataster_S': 'string',
        'Kataster_H': 'string',
        'Kataster13': 'float',
        'Kataster15': 'float',
        'Kataster_E': 'string'}).set_index('Kataster_C')

bestand.index.names = ['id']

bestand['address'] = bestand['Kataster_S'] + ' ' + bestand['Kataster_H']
bestand = bestand.drop('Kataster_S', 1)
bestand = bestand.drop('Kataster_H', 1)
bestand = bestand.rename(columns = {'Kataster13': 'spec_heat_consumption', 'Kataster15': 'spec_power_consumption', 'Kataster_E': 'energy_source'})

# Neubau:
neubau = read_shapefile(
    "../data/GIS/Shapefiles/Neubau Gebaeude Kataster.shp", columns={
        'Kataster_C': 'string',
        'Kataster_S': 'string',
        'Kataster13': 'float',
        'Kataster15': 'float'}).set_index('Kataster_C')

neubau.index.names = ['id']

neubau = neubau.rename(columns={'Kataster_S': 'address', 'Kataster13': 'spec_heat_consumption', 'Kataster15': 'spec_power_consumption'})

# merge:
# buildings = buildings = pandas.concat([bestand, neubau])
buildings = buildings = bestand

# adjust data
buildings['spec_heat_consumption'] = buildings['spec_heat_consumption'].fillna(0).to_numpy()
buildings['spec_power_consumption'] = buildings['spec_power_consumption'].fillna(0).to_numpy()

# generic data
buildings['CO2'] = (buildings['spec_heat_consumption'] + buildings['spec_power_consumption']) / 20000
electricity_supply_types = ['green', 'gray', 'mix']
buildings['electricity_supplier'] = [electricity_supply_types[random.randint(0,2)] for row in buildings.values]
buildings['connection_to_heat_grid'] = buildings['energy_source'].isna().to_numpy()
buildings['refurbished'] = buildings['connection_to_heat_grid']
buildings['environmental_engagement'] = [random.random() for row in buildings.values]

# buildings interaction
buildings['cell'] = ""
buildings['selected'] = False
buildings['group'] = -1

bd = buildings.sample(50)
bd['connection_to_heat_grid'] = random.randint(2020, 2045)
buildings.update(bd)

with pandas.option_context('display.max_rows', None,
                        'display.max_columns', None,
                        'display.precision', 3,
                        ):
    print(buildings)

make_groups(buildings)

print("end")