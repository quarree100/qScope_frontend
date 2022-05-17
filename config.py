config = {
    'BASEMAP_FILE': "../data/GIS/Layer/180111-QUARREE100-RK_modifiziert_smaller.jpg",
    'GEBAEUDE_BESTAND_FILE': "../data/GIS/Shapefiles/bestandsgebaeude_export.shp",
    'GEBAEUDE_NEUBAU_FILE': "../data/GIS/Shapefiles/Neubau Gebaeude Kataster.shp",
    'WAERMESPEICHER_FILE': "../data/GIS/Shapefiles/Waermespeicher.shp",
    'HEIZZENTRALE_FILE': "../data/GIS/Shapefiles/Heizzentrale.shp",
    'NAHWAERMENETZ_FILE': "../data/GIS/Shapefiles/Nahwaermenetz.shp",
    'TYPOLOGIEZONEN_FILE': "../data/GIS/Shapefiles/Typologiezonen.shp",

    'CSPY_SETTINGS_FILE': '../cspy/settings/cityscopy.json',
    'SAVED_KEYSTONE_FILE': 'keystone.save',
    'SAVED_BUILDINGS_FILE': 'export/buildings_export.shp',

    'GAMA_HEADLESS_FOLDER' : '../data/headless/',
    'GAMA_MODEL_FILE' : '../q100_abm/q100/models/qscope_ABM.gaml',

    'GRID_1_SETUP_FILE': '../data/grid_1_setup.csv',
    'GRID_2_SETUP_FILE': '../data/grid_2_setup.csv',
    'GRID_1_INPUT_ENVIRONMENT_FILE': '../data/input_environment_grid_1.csv',
    'GRID_2_INPUT_ENVIRONMENT_FILE': '../data/input_environment_grid_2.csv',

    'GRID_2_X1' : 50,
    'GRID_2_X2' : 100,
    'GRID_2_Y1' : 0,
    'GRID_2_Y2' : 81.818,

    'GRID_1_X1' : 0,
    'GRID_1_X2' : 50,
    'GRID_1_Y1' : 0,
    'GRID_1_Y2' : 81.818
}


# TODO: replace grid_x_setup.csv with mode names: input_mode.csv ? so each mode is customizable by an according csv