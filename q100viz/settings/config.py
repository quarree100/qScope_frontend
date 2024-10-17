import os

DATA_FOLDER = "./data" # change me

DATA_ABS_PATH = os.path.abspath(DATA_FOLDER)

config = {
    # UDP communication
    'UDP_SERVER_PORT' : 8081,
    
    # GIS files
    'BASEMAP_FILE': os.path.join(DATA_ABS_PATH, "GIS/180111-QUARREE100-RK_modifiziert_smaller.jpg"),
    'GEBAEUDE_BESTAND_FILE': os.path.join(DATA_ABS_PATH, "GIS/Ruesdorfer_Kamp.shp"),
    # 'GEBAEUDE_NEUBAU_FILE': os.path.join(DATA_ABS_PATH, "GIS/Shapefiles/Neubau Gebaeude Kataster.shp"),
    # 'WAERMESPEICHER_FILE': os.path.join(DATA_ABS_PATH, "GIS/Shapefiles/Waermespeicher.shp"),
    'NAHWAERMENETZ_FILE': os.path.join(DATA_ABS_PATH, "GIS/Nahwaermenetz.shp"),

    # graphics setup
    'SAVED_KEYSTONE_FILE': 'keystone.save',
    'SAVED_BUILDINGS_FILE': 'export/buildings_export.shp',
    'CANVAS_SIZE' : (3840, 2160),

    # game rules
    'NUM_OF_ROUNDS' : 4,
    'NUM_OF_USERS' : 4,

    # simulation
    # 'GAMA_HEADLESS_FOLDER' : '/opt/gama-platform/headless/',
    'GAMA_HEADLESS_FOLDER' : '/home/qscope/opt/GAMA_1.9.2/headless/',
    'GAMA_OUTPUT_FOLDER': os.path.join(DATA_ABS_PATH, 'outputs/output'),
    'GAMA_MODEL_FILE' : '../q100_abm_qscope-workshop/q100/models/qscope_ABM.gaml',
    'SIMULATION_FORCE_START_YEAR' : 2020,
    'SIMULATION_FORCE_END_YEAR' : 2030,
    'REFERENCE_DATA_FOLDER' : os.path.join(DATA_ABS_PATH, 'precomputed/simulation_defaults'),

    # grid setup
    'CSPY_SETTINGS_FILE': '../cspy/settings/qscope_L.json',
    'GRID_1_SETUP_FILE': 'q100viz/settings/buildings_interaction_grid_1.csv',
    'GRID_2_SETUP_FILE': 'q100viz/settings/buildings_interaction_grid_2.csv',
    'GRID_1_INPUT_SCENARIOS_FILE': 'q100viz/settings/buildings_interaction_grid_1.csv',
    'GRID_2_INPUT_SCENARIOS_FILE': 'q100viz/settings/buildings_interaction_grid_2.csv',
    'GRID_1_INDIVIDUAL_DATA_VIEW_FILE': 'q100viz/settings/individual_data_view_grid_1.csv',
    'GRID_2_INDIVIDUAL_DATA_VIEW_FILE': 'q100viz/settings/individual_data_view_grid_2.csv',
    'GRID_1_TOTAL_DATA_VIEW_FILE': 'q100viz/settings/total_data_view_grid_1.csv',
    'GRID_2_TOTAL_DATA_VIEW_FILE': 'q100viz/settings/total_data_view_grid_2.csv'

}
