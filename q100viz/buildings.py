import pandas
import random
import shapely
import pygame
import json

import q100viz.session as session
import q100viz.devtools as devtools
import q100viz.gis as gis
import q100viz.api as api
from q100viz.settings.config import config

class Buildings:
    def __init__(self):
        self.df = pandas.DataFrame()
        self.df['energy_source'] = None

    ########################### Load data #############################
    def load_data(self, create_clusters=False):
        # Bestand:
        bestand = gis.read_shapefile(
            config['GEBAEUDE_BESTAND_FILE'], columns={
                'Kataster_C': 'string',  # Code
                'Kataster_S': 'string',  # Straße
                'Kataster_H': 'string',  # Hausnummer
                # 'Kataster_B': 'float',  # Baujahr
                'Kataster_6': 'float',  # Nettogrundfläche
                'Kataster13': 'float',  # spez. Wärmeverbrauch
                'Kataster15': 'float',  # spez. Stromverbrauch
                'Kataster_E': 'string',  # Energieträger
                'Kataster_A': 'string',  # Gebäudetyp
                'Kataster_W' : 'int'
                }).set_index('Kataster_C')

        bestand.index.names = ['id']

        bestand['address'] = bestand['Kataster_S'] + ' ' + bestand['Kataster_H']
        bestand = bestand.drop('Kataster_S', axis=1)
        bestand = bestand.drop('Kataster_H', axis=1)
        bestand = bestand.rename(columns = {
            'Kataster13': 'spec_heat_consumption',
            'Kataster15': 'spec_power_consumption',
            'Kataster_E': 'energy_source',
            'Kataster_A' : 'type',
            'Kataster_6' : 'area',
            'Kataster_W' : 'units'})

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
        self.df['spec_power_consumption'] = self.df['spec_power_consumption'].fillna(0).to_numpy()
        self.df['cluster_size'] = 0

        # make clusters and get average cluster data:
        if create_clusters:
            self.df['avg_spec_power_consumption'] = 0
            self.df['avg_spec_heat_consumption'] = 0
            buildings_cluster = self.make_clusters(start_interval=0.5)
            for j in range(len(self.df)):
                self.df.at[self.df.index[j], 'avg_spec_heat_consumption'] = buildings_cluster[j]['spec_heat_consumption'].mean()
                self.df.at[self.df.index[j], 'avg_spec_power_consumption'] = buildings_cluster[j]['spec_power_consumption'].mean()
                self.df.at[self.df.index[j], 'cluster_size'] = int(len(buildings_cluster[j]))

        # add initial graphs (path relative for infoscreen):
        self.df['emissions_graphs'] = ''
        self.df['energy_prices_graphs'] = ''
        for idx in self.df.index:
            self.df.at[idx, 'emissions_graphs'] = "img/blank_16x12inches.png".format(idx)
            self.df.at[idx, 'energy_prices_graphs'] = "img/blank_16x12inches.png".format(idx)

        # generic data
        for idx, row in self.df.iterrows():
            self.df.at[idx, 'connection_to_heat_grid'] = 2020 if self.df.loc[idx, 'energy_source'] is None else False  # note: we decided that all buildings without any energy_source in the source data are set pre-connected.
        self.df['connection_to_heat_grid_prior'] = self.df['connection_to_heat_grid']
        self.df['refurbished'] = self.df['connection_to_heat_grid']
        self.df['refurbished_prior'] = self.df['refurbished']
        self.df['save_energy'] = False
        self.df['save_energy_prior'] = self.df['save_energy']

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
            points = session._gis.surface.transform(polygon.exterior.coords)
            pygame.draw.polygon(session._gis.surface, pygame.Color(255,123,222), points)

            poly = shapely.geometry.Polygon(points)
            centroid = poly.centroid

            shortest_dist = 9999999

            for linestring in session._gis.nahwaermenetz.to_dict('records'):
                line_points = session._gis.surface.transform(linestring['geometry'].coords)
                line = shapely.geometry.LineString(line_points)

                interpol = line.interpolate(line.project(centroid))

                this_dist = interpol.distance(centroid)
                if this_dist < shortest_dist:
                    shortest_dist = this_dist
                    self.df.at[idx, 'target_point'] = interpol

        if print_full_df:
            devtools.print_full_df(self.df)

    ############################# user groups #########################
    def list_from_groups(self):
        '''returns a list with of buildings with 'group' >= 0; one df for each user group'''
        return [
            self.df[self.df['group'] == 0][session.COMMUNICATION_RELEVANT_KEYS],
            self.df[self.df['group'] == 1][session.COMMUNICATION_RELEVANT_KEYS],
            self.df[self.df['group'] == 2][session.COMMUNICATION_RELEVANT_KEYS],
            self.df[self.df['group'] == 3][session.COMMUNICATION_RELEVANT_KEYS]]

    def get_dict_with_api_wrapper(self):

        wrapper = ['' for i in range(session.num_of_users)]
        message = {}

        for i, group_df in enumerate(self.list_from_groups()):
            group_wrapper = {}
            if len(group_df) > 0:
                user_selected_buildings = json.loads(
                    api.export_json(group_df[session.COMMUNICATION_RELEVANT_KEYS], None))
                group_wrapper['buildings'] = user_selected_buildings
                group_wrapper['connections'] = len(group_df[group_df['connection_to_heat_grid'] != False])
                group_wrapper['slider_handles'] = []
                for sliders in session.grid_1.sliders, session.grid_2.sliders:
                    for slider in sliders.values():
                        if slider.group == i and slider.handle is not None:
                            group_wrapper['slider_handles'].append(slider.handle)

                message['group_{0}'.format(str(i))] = group_wrapper
            else:  # create empty elements for empty groups (infoscreen reset)
                message['group_{0}'.format(str(i))] = ['']

            wrapper = {
                'buildings_groups': message
            }

        return wrapper

    ############################## clusters ###########################
    def make_clusters(self, start_interval):
        '''make groups of the selected buildings. group by standard deviation of energy consumption'''
        cluster_list = []
        for idx in range(len(self.df.index)):
            interval = start_interval  # standard deviation
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
            session.log += ("\n" +
                devtools.print_verbose(
                "building {0} is in a group of to {1} buildings with similar specs:".format(self.df.index[idx], len(cluster)), session.VERBOSE_MODE))
            # devtools.print_verbose(cluster[['spec_heat_consumption', 'spec_power_consumption']].describe(), session.VERBOSE_MODE)

        return cluster_list

    ################### allocate random buildings #####################
    def allocate_random_groups(self, n):
        '''sets group to random[0, n] for each building'''
        for idx, row in self.df.iterrows():
            self.df.at[idx, 'group'] = random.randint(0, n)