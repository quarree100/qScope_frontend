config = {
    # UDP communication
    'UDP_SERVER_PORT' : 8081,
    'UDP_TABLE_1' : 5001,
    'UDP_TABLE_2' : 5000,

    # GIS files
    'BASEMAP_FILE': "../data/GIS/Layer/180111-QUARREE100-RK_modifiziert_smaller.jpg",
    'GEBAEUDE_BESTAND_FILE': "../data/GIS/Shapefiles/bestandsgebaeude_export.shp",
    'GEBAEUDE_NEUBAU_FILE': "../data/GIS/Shapefiles/Neubau Gebaeude Kataster.shp",
    'WAERMESPEICHER_FILE': "../data/GIS/Shapefiles/Waermespeicher.shp",
    'NAHWAERMENETZ_FILE': "../data/GIS/Shapefiles/Nahwaermenetz.shp",

    # graphics setup
    'SAVED_KEYSTONE_FILE': 'keystone.save',
    'SAVED_BUILDINGS_FILE': 'export/buildings_export.shp',
    'CANVAS_SIZE' : (1920, 1080),

    # game rules
    'NUM_OF_ROUNDS' : 4,
    'NUM_OF_USERS' : 4,

    # simulation
    # 'GAMA_HEADLESS_FOLDER' : '/opt/gama-platform/headless/',
    'GAMA_HEADLESS_FOLDER' : '/home/qscope/opt/GAMA_1.9.2/headless/',
    'GAMA_OUTPUT_FOLDER': '../data/outputs/output',
    'GAMA_MODEL_FILE' : '../q100_abm_qscope-workshop/q100/models/qscope_ABM.gaml',
    'SIMULATION_FORCE_START_YEAR' : 2020,
    'SIMULATION_FORCE_END_YEAR' : 2030,
    'REFERENCE_DATA_FOLDER' : '../data/precomputed/simulation_defaults',

    # grid setup
    'CSPY_SETTINGS_FILE': '../cspy/settings/qscope_L.json',
    'GRID_1_SETUP_FILE': 'q100viz/settings/buildings_interaction_grid_1.csv',
    'GRID_2_SETUP_FILE': 'q100viz/settings/buildings_interaction_grid_2.csv',
    'GRID_1_INPUT_SCENARIOS_FILE': 'q100viz/settings/buildings_interaction_grid_1.csv',
    'GRID_2_INPUT_SCENARIOS_FILE': 'q100viz/settings/buildings_interaction_grid_2.csv',
    'GRID_1_INDIVIDUAL_DATA_VIEW_FILE': 'q100viz/settings/individual_data_view_grid_1.csv',
    'GRID_2_INDIVIDUAL_DATA_VIEW_FILE': 'q100viz/settings/individual_data_view_grid_2.csv',
    'GRID_1_TOTAL_DATA_VIEW_FILE': 'q100viz/settings/total_data_view_grid_1.csv',
    'GRID_2_TOTAL_DATA_VIEW_FILE': 'q100viz/settings/total_data_view_grid_2.csv',

    # physical grid extents, in percent:
    'GRID_2_X1' : 50,
    'GRID_2_X2' : 100,
    'GRID_2_Y1' : 0,
    'GRID_2_Y2' : 86.27,

    'GRID_1_X1' : 0,
    'GRID_1_X2' : 50,
    'GRID_1_Y1' : 0,
    'GRID_1_Y2' : 86.27,

    # interaction tuning
    'buildings_selection_mode': 'rotation' # select 'all' intersected buildings or choose by 'rotation'

}

config_slider = {
    'slider0' :
        {
            'PHYSICAL_SLIDER_AREA_LENGTH' : 38.6,
            'PHYSICAL_DIFF_L' : 5.0,
            'PHYSICAL_DIFF_R' : 32.0,
        },
    'slider1' :
        {
            'PHYSICAL_SLIDER_AREA_LENGTH' : 38.6,
            'PHYSICAL_DIFF_L' : 6.6,
            'PHYSICAL_DIFF_R' : 31.6,
        },
    'slider2' :
        {
            'PHYSICAL_SLIDER_AREA_LENGTH' : 38.6,
            'PHYSICAL_DIFF_L' : 4.7,
            'PHYSICAL_DIFF_R' : 30.1,
        },
    'slider3' :
        {
            'PHYSICAL_SLIDER_AREA_LENGTH' : 38.6,
            'PHYSICAL_DIFF_L' : 7.0,
            'PHYSICAL_DIFF_R' : 31.5,
        },

}