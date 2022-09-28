import pandas
import random
import shapely
import pygame
import json

import q100viz.session as session
import q100viz.gis as gis
import q100viz.api as api
from q100viz.settings.config import config

class Buildings:
    def __init__(self):
        self.df = pandas.DataFrame()
        self.df['energy_source'] = None

    ########################### Load data #############################
    def load_data(self):
        # Bestand:
        bestand = gis.read_shapefile(
            config['GEBAEUDE_BESTAND_FILE'], columns={
                'Kataster_C': 'string',  # Code
                'Kataster_S': 'string',  # Straße
                'Kataster_H': 'string',  # Hausnummer
                # 'Kataster_B': 'float',  # Baujahr
                # 'Kataster_6': 'float',  # Nettogrundfläche
                'Kataster13': 'float',  # spez. Wärmeverbrauch
                'Kataster15': 'float',  # spez. Stromverbrauch
                'Kataster_E': 'string'  # Energieträger
                }).set_index('Kataster_C')

        bestand.index.names = ['id']

        bestand['address'] = bestand['Kataster_S'] + ' ' + bestand['Kataster_H']
        bestand = bestand.drop('Kataster_S', 1)
        bestand = bestand.drop('Kataster_H', 1)
        bestand = bestand.rename(columns = {'Kataster13': 'spec_heat_consumption', 'Kataster15': 'spec_power_consumption', 'Kataster_E': 'energy_source'})

        # bestand['area'] = bestand['Kataster_6'].fillna(0).to_numpy()
        # bestand = bestand.drop('Kataster_6', 1)

        # bestand['year'] = bestand['Kataster_B']
        # bestand['year'] = bestand['year'].fillna(0).to_numpy().astype(int)
        # bestand = bestand.drop('Kataster_B', 1)

        # Neubau:
        # neubau = gis.read_shapefile(
        #     config['GEBAEUDE_NEUBAU_FILE'], columns={
        #         'Kataster_C': 'string',
        #         'Kataster_S': 'string',
        #         'Kataster13': 'float',
        #         'Kataster15': 'float'}).set_index('Kataster_C')

        # neubau.index.names = ['id']

        # neubau = neubau.rename(columns={'Kataster_S': 'address', 'Kataster13': 'spec_heat_consumption', 'Kataster15': 'spec_power_consumption'})

        # merge:
        # buildings = session.buildings = pandas.concat([bestand, neubau])
        self.df = bestand

        # adjust data
        self.df['spec_heat_consumption'] = self.df['spec_heat_consumption'].fillna(0).to_numpy()
        self.df['avg_spec_heat_consumption'] = 0
        self.df['spec_power_consumption'] = self.df['spec_power_consumption'].fillna(0).to_numpy()
        self.df['avg_spec_power_consumption'] = 0
        self.df['cluster_size'] = 0

        buildings_cluster = self.make_clusters()
        # update building with average data:
        for j in range(len(self.df)):
            self.df.at[self.df.index[j], 'avg_spec_heat_consumption'] = buildings_cluster[j]['spec_heat_consumption'].mean()
            self.df.at[self.df.index[j], 'avg_spec_power_consumption'] = buildings_cluster[j]['spec_power_consumption'].mean()
            self.df.at[self.df.index[j], 'cluster_size'] = int(len(buildings_cluster[j]))

        self.df['emissions_graphs'] = ''
        self.df['energy_prices_graphs'] = ''

        # generic data
        self.df['CO2'] = (self.df['spec_heat_consumption'] + self.df['spec_power_consumption']) / 20000
        electricity_supply_types = ['green', 'gray', 'mix']
        self.df['electricity_supplier'] = [electricity_supply_types[random.randint(0,2)] for row in self.df.values]
        for idx, row in self.df.iterrows():
            self.df.at[idx, 'connection_to_heat_grid'] = 2020 if self.df.loc[idx, 'energy_source'] is None else False
        self.df['connection_to_heat_grid_prior'] = self.df['connection_to_heat_grid']
        self.df['refurbished'] = self.df['connection_to_heat_grid']
        self.df['refurbished_prior'] = self.df['refurbished']
        self.df['environmental_engagement'] = [True if random.random() > 0.5 else False for row in self.df.values]
        self.df['environmental_engagement_prior'] = self.df['environmental_engagement']

        # buildings interaction
        self.df['cell'] = ""
        self.df['selected'] = False
        self.df['group'] = -1

        self.find_closest_heat_grid_line(print_full_df=False)

        return self.df

    ##################### find closest heat grid line #################
    def find_closest_heat_grid_line(self, print_full_df):
        self.df['target_point'] = None

        for idx, row in self.df.iterrows():
            polygon = row['geometry']
            points = session.gis.surface.transform(polygon.exterior.coords)
            pygame.draw.polygon(session.gis.surface, pygame.Color(255,123,222), points)

            poly = shapely.geometry.Polygon(points)
            centroid = poly.centroid

            shortest_dist = 9999999

            for linestring in session.gis.nahwaermenetz.to_dict('records'):
                line_points = session.gis.surface.transform(linestring['geometry'].coords)
                line = shapely.geometry.LineString(line_points)

                interpol = line.interpolate(line.project(centroid))

                this_dist = interpol.distance(centroid)
                if this_dist < shortest_dist:
                    shortest_dist = this_dist
                    self.df.at[idx, 'target_point'] = interpol

        if print_full_df:
            api.print_full_df(self.df)

    ############################# user groups #########################
    def make_buildings_groups_dict(self):

        session.buildings_groups_list = [
            self.df[self.df['group'] == 0][session.COMMUNICATION_RELEVANT_KEYS],
            self.df[self.df['group'] == 1][session.COMMUNICATION_RELEVANT_KEYS],
            self.df[self.df['group'] == 2][session.COMMUNICATION_RELEVANT_KEYS],
            self.df[self.df['group'] == 3][session.COMMUNICATION_RELEVANT_KEYS]]

        wrapper = ['' for i in range(session.num_of_users)]
        message = {}

        for i, group_df in enumerate(session.buildings_groups_list):
            group_wrapper = {}
            if len(group_df) > 0:
                user_selected_buildings = json.loads(
                    api.export_json(group_df[session.COMMUNICATION_RELEVANT_KEYS], None))
                group_wrapper['buildings'] = user_selected_buildings
                group_wrapper['connections'] = len(group_df[group_df['connection_to_heat_grid'] != False])

                message['group_{0}'.format(str(i))] = group_wrapper
            else:  # create empty elements for empty groups (infoscreen reset)
                message['group_{0}'.format(str(i))] = ['']

            wrapper = {
                'buildings_groups': message
            }

        return wrapper

    ############################## clusters ###########################
    def make_clusters(self):
        '''make groups of the selected buildings. group by standard deviation of energy consumption'''
        cluster_list = []
        for idx in range(len(self.df.index)):
            interval = 0.5  # standard deviation
            cluster = pandas.DataFrame()
            while len(cluster) < 2:  # make sure no building is alone
                cluster = self.df.loc[(
                        (self.df['energy_source'] == self.df.loc[
                            self.df.index[idx], 'energy_source'])
                        &
                        (self.df['spec_heat_consumption'] >= self.df.loc[self.df.index[idx],
                        'spec_heat_consumption'] - self.df['spec_heat_consumption'].std() * interval)
                        &
                        (self.df['spec_heat_consumption'] <= self.df.loc[self.df.index[idx],
                        'spec_heat_consumption'] + self.df['spec_heat_consumption'].std() * interval)
                        &
                        (self.df['spec_power_consumption'] >= self.df.loc[self.df.index[idx],
                        'spec_power_consumption'] - self.df['spec_power_consumption'].std() * interval)
                        &
                        (self.df['spec_power_consumption'] <= self.df.loc[self.df.index[idx],
                        'spec_power_consumption'] + self.df['spec_power_consumption'].std() * interval)
                    )]
                interval += 0.1  # increase range, try again if necessary

            cluster_list.append(cluster)
            session.print_verbose(
                "building {0} is in a group of to {1} buildings with similar specs:".format(self.df.index[idx], len(cluster)))
            # session.print_verbose(cluster[['spec_heat_consumption', 'spec_power_consumption']].describe())

        return cluster_list
