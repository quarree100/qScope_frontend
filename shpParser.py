# Skript zum Vorbereiten von Geodaten für Processing:
# Konvertiert ESRI .shp Dateien zu .csv
#
# Ausgewählte Funktionen werden am Ende des Skripts ausgeführt.
# Die Funktionen sind Eingangsdaten-spezifisch, d.h. sie sind auf eine genaue
#   Konvertierung und Formatierung zugeschnitten.
# output format is .csv table for further use in Processing etc.
#
# David Unland, Oktober-Dezember 2019
# unland[at]uni-bremen.de
###############################################################################

import numpy as np
import geopandas
import pandas as pd

folder = '/home/dav/res/00_dokumente/QGIS/Shapefiles/'
file = 'osm_heide_buildings.shp'
output = 'output.csv'

# functions are run at the end of the script...


# %% -----------------load all functions---------------------------------------
# --------------------------------functions------------------------------------
def test1(inputfile, outputfile):
    osm_heide_buildings = geopandas.read_file(inputfile)
    osm_heide_buildings.keys()
    osm_heide_buildings

    type(osm_heide_buildings)

    stettiner = osm_heide_buildings[osm_heide_buildings['addr_stree']
                                    == 'Stettiner Straße']
    stettiner

    for i in range(len(osm_heide_buildings.full_id)):
        if int(osm_heide_buildings.iloc[i]['osm_id']) >= 167078604:
            print(osm_heide_buildings.iloc[i]['full_id'])
        else:
            print('nö')

    osm_heide_buildings = osm_heide_buildings[['full_id', 'osm_id']]

    osm_heide_buildings[osm_heide_buildings['osm_id']
                        == '167224172'].iloc[0].loc['full_id']

    new = osm_heide_buildings[osm_heide_buildings['osm_id'] == '167224172']
    new.iloc[0].loc['full_id']


def export_osm_heide_buildings(inputfile, outputfile):
    # folder = '/home/dav/res/00_dokumente/QGIS/Shapefiles/'
    # file = 'osm_heide_buildings.shp'
    osm_heide_buildings = geopandas.read_file(inputfile)

    polygons = osm_heide_buildings['geometry']

    pol_df = pd.DataFrame(columns=['long', 'lat'])
    for i in range(len(polygons)):
        pol = polygons.iloc[i]
        pol_list = pd.DataFrame(list(pol.exterior.coords), columns=['long', 'lat'])
        # pol_df = pd.concat([pol_df, pd.Series(pol_list)]) # output is set of (long, lat) per row
        pol_df = pol_df.append(pol_list)

    pol_df[:50]
    pol_df.to_csv('shapes_pde/osm_heide_buildings.csv')
    pol_df.to_csv('shapes_pde/stettiner.csv')

    max(pol_df['lat'])  # 54.1988598
    max(pol_df['long'])  # 9.1143553

    min(pol_df['lat'])  # 54.1876916
    min(pol_df['long'])  # 9.0975364


# transform to epsg3857 with units in [metres]
def convert_osm_heide_buildings_to_epsg3857(inputfile, outputfile):
    osm_heide_buildings = geopandas.read_file(inputfile)
    osm_heide_buildings.crs
    osm_heide_buildings.head(2)
    osm_heide_buildings = osm_heide_buildings.to_crs({'init': 'epsg:3857'})
    polygons = osm_heide_buildings['geometry']

    pol_df = pd.DataFrame(columns=['long', 'lat'])
    for i in range(len(polygons)):
        pol = polygons.iloc[i]
        pol_list = pd.DataFrame(list(pol.exterior.coords), columns=['long', 'lat'])
        # pol_df = pd.concat([pol_df, pd.Series(pol_list)]) # output is set of (long, lat) per row
        pol_df = pol_df.append(pol_list)

    pol_df[:50]

    pol_df.to_csv('shapes_pde/shapes_3857.csv')

    max(pol_df['lat'])  # 7207908.279847572
    max(pol_df['long'])  # 1014605.3909049741

    min(pol_df['lat'])  # 7205783.278099706
    min(pol_df['long'])  # 1012733.1195212711


# merging additional data to dataFrame with lats + lons as Strings
def mergeAndConvert_osm_heide_buildings(inputfile, outputfile):
    osm_heide_buildings = geopandas.read_file(inputfile)
    osm_heide_buildings = osm_heide_buildings.to_crs(
        {'init': 'epsg:3857'})  # convert to epsg3857

    table = pd.DataFrame(columns=['id', 'osm_id', 'lons', 'lats'])
    table['osm_id'] = osm_heide_buildings['osm_id']
    table

    polygons = osm_heide_buildings['geometry']

    maxLat = 0
    maxLon = 0
    minLon = np.inf
    minLat = np.inf
    for n in range(len(polygons)):
        pol_list = pd.DataFrame(list(polygons[n].exterior.coords), columns=[
                                'long', 'lat'])  # geometry to df

        lons = ''  # df to Strings
        for element in pol_list['long']:
            lons += str(element) + ' '
            if element > maxLon:
                maxLon = element
            if element < minLon:
                minLon = element

        lats = ''
        for element in pol_list['lat']:
            lats += str(element) + ' '
            if element > maxLat:
                maxLat = element
            if element < minLat:
                minLat = element

        table.at[n, 'lats'] = lats  # add data to table
        table.at[n, 'lons'] = lons

    maxLat  # 7207334.989219683
    maxLon  # 1013901.5511605354

    minLat  # 7206217.947052765
    minLon  # 1013137.0311616653

    table['id'] = range(len(polygons))
    table
    gebaeudeliste_import = pd.read_csv('Gebaeudeliste_import.csv',
                                       delimiter=';')
    table['osm_id'] = table['osm_id'].astype(int)

    table = table.merge(gebaeudeliste_import, on='osm_id', how='left')
    table
    table.to_csv(outputfile)


# converts area polygons to format:
# osm_ID | list of latitudes | list of longitudes
def convertTypologiezonen(inputfile, outputfile):
    typologiezonen = geopandas.read_file(inputfile)
    typologiezonen.keys()
    ids = pd.DataFrame(typologiezonen.id)
    ids
    polygons = typologiezonen.geometry

    polygons_table = pd.DataFrame(
        columns=['id', 'lons', 'lats'])  # container for results
    for n in range(len(polygons)):
        pol_list = pd.DataFrame(list(polygons[n].exterior.coords), columns=[
                                'long', 'lat'])  # geometry to df

        lons = ''  # df to Strings with values separated by spaces
        for element in pol_list['long']:
            lons += str(element) + ' '

        lats = ''
        for element in pol_list['lat']:
            lats += str(element) + ' '

        polygons_table.at[n, 'lats'] = lats  # add data to table
        polygons_table.at[n, 'lons'] = lons

    polygons_table.index = typologiezonen.id
    print(polygons_table)
    polygons_table.to_csv(outputfile)


# import Wärmenetz
# lineStrings are of shape (long lat, long lat, ...)
def convertNahwaermenetz(inputfile, outputfile):
    nahwaermenetz = geopandas.read_file(inputfile)
    polygons = nahwaermenetz.geometry

    polygons_table = pd.DataFrame(
        columns=['id', 'lons', 'lats'])  # container for results
    for n in range(len(polygons)):  # go into geometry

        pol_list = pd.DataFrame(list(polygons[n].coords), columns=[
                                'long', 'lat'])  # geometry to df

        lons = ''  # df to Strings with values separated by spaces
        for element in pol_list['long']:
            lons += str(element) + ' '

        lats = ''
        for element in pol_list['lat']:
            lats += str(element) + ' '

        polygons_table.at[n, 'lats'] = lats  # add data to table
        polygons_table.at[n, 'lons'] = lons

    polygons_table
    polygons_table.id = range(len(polygons_table))
    polygons_table.to_csv(outputfile)


# % ---------------------------------------------------------------------------
# import Wärmespeicher + Heizzentrale
def convertWaermespeicherHeizzentrale(inputfiles_list, outputfile):
    # waermespeicher = geopandas.read_file('/home/dav/res/00_dokumente/QGIS/Shapefiles/Wärmespeicher.shp')
    # heizzentrale = geopandas.read_file('/home/dav/res/00_dokumente/QGIS/Shapefiles/Heizzentrale.shp')

    waermespeicher, heizzentrale = geopandas.read_file(inputfiles_list)

    polygons_table = pd.DataFrame(columns=['id', 'name', 'lons', 'lats'])  # table to store results
    polygons_table['id'] = [0,1]
    n = 0  # index for table position
    for data in (waermespeicher, heizzentrale):
        geom = data.geometry
        g = [i for i in geom]
        x, y = g[0].exterior.coords.xy

        # create space separated values for lats and lons
        lons = ''
        for i in x:
            lons += str(i) + ' '

        lats = ''
        for i in y:
            lats += str(i) + ' '

        polygons_table.at[n, 'lons'] = lons
        polygons_table.at[n, 'lats'] = lats
        polygons_table.at[n, 'name'] = data.Name[0]

        n += 1

    polygons_table
    polygons_table.to_csv(outputfile)


# %% -------------------------------- run selected functions-------------------
convertWaermespeicherHeizzentrale([folder+'Wärmespeicher.shp',
                                   folder+'Heizzentrale.shp'], output)
