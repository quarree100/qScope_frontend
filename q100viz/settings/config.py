import os

DATA_FOLDER = "../data" # change me

DATA_ABS_PATH = os.path.abspath(DATA_FOLDER)

config = {
    'DATA_ABS_PATH' : DATA_ABS_PATH,
    # Infoscreen communication
    'UDP_SERVER_PORT' : 8081,
    'HTTP_SERVER_PORT' : 8082,
    # TUIO Touch Table
    'TUIO_ADDRESS' : '10.42.0.1', # 'localhost', when using TUIOSimulator
    'TUIO_PORT' : 3333,
    
    # GIS files
    'BASEMAP_FILE': os.path.join(DATA_ABS_PATH, "GIS/Layer/180111-QUARREE100-RK_modifiziert_smaller.jpg"),
    'GEBAEUDE_BESTAND_FILE': os.path.join(DATA_ABS_PATH, "GIS/Shapefiles/bestandsgebaeude_export.shp"),
    'GEBAEUDE_NEUBAU_FILE': os.path.join(DATA_ABS_PATH, "GIS/Shapefiles/Neubau Gebaeude Kataster.shp"),
    'WAERMESPEICHER_FILE': os.path.join(DATA_ABS_PATH, "GIS/Shapefiles/Waermespeicher.shp"),
    'NAHWAERMENETZ_FILE': os.path.join(DATA_ABS_PATH, "GIS/Shapefiles/Nahwaermenetz.shp"),

    # graphics setup
    'SAVED_KEYSTONE_FILE': 'keystone.save',
    'SAVED_BUILDINGS_FILE': 'export/buildings_export.shp',
    'CANVAS_SIZE' : (3840, 2160),

    # game rules
    'NUM_OF_ROUNDS' : 4,
    'NUM_OF_USERS' : 4,

    # simulation
    # 'GAMA_HEADLESS_FOLDER' : '/opt/gama-platform/headless/',
    'GAMA_HEADLESS_FOLDER' : '../GAMA_1.9.2_Linux_with_JDK/headless/',
    'GAMA_OUTPUT_FOLDER': os.path.join(DATA_ABS_PATH, 'outputs/output'),
    'GAMA_MODEL_FILE' : '../q100_abm_qscope-workshop/q100/models/qscope_ABM.gaml',
    'SIMULATION_INITIAL_VARIABLES' : '../data/includes/csv-data_technical/initial_variables.csv',
    'SIMULATION_FORCE_START_YEAR' : 2020,
    'SIMULATION_FORCE_END_YEAR' : 2045,
    'REFERENCE_DATA_FOLDER' : os.path.join(DATA_ABS_PATH, 'precomputed/simulation_defaults'),

}
