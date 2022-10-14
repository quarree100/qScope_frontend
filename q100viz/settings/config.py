config = {
    # GIS files
    'BASEMAP_FILE': "../data/GIS/Layer/180111-QUARREE100-RK_modifiziert_smaller.jpg",
    'GEBAEUDE_BESTAND_FILE': "../data/GIS/Shapefiles/bestandsgebaeude_export.shp",
    'GEBAEUDE_NEUBAU_FILE': "../data/GIS/Shapefiles/Neubau Gebaeude Kataster.shp",
    'WAERMESPEICHER_FILE': "../data/GIS/Shapefiles/Waermespeicher.shp",
    'HEIZZENTRALE_FILE': "../data/GIS/Shapefiles/Heizzentrale.shp",
    'NAHWAERMENETZ_FILE': "../data/GIS/Shapefiles/Nahwaermenetz.shp",
    'TYPOLOGIEZONEN_FILE': "../data/GIS/Shapefiles/Typologiezonen.shp",

    # graphics setup
    'SAVED_KEYSTONE_FILE': 'keystone.save',
    'SAVED_BUILDINGS_FILE': 'export/buildings_export.shp',

    # simulation files
    'GAMA_HEADLESS_FOLDER' : '/opt/gama-platform/headless/',
    'GAMA_OUTPUT_FOLDER': '../data/outputs/output',
    'GAMA_MODEL_FILE' : '../q100_abm_qscope-workshop/q100/models/qscope_ABM.gaml',
    'SIMULATION_FORCE_MAX_YEAR' : 0,

    # grid setup
    'CSPY_SETTINGS_FILE': '../data/cityscopy.json',
    'GRID_1_SETUP_FILE': 'q100viz/settings/buildings_interaction_grid_1.csv',
    'GRID_2_SETUP_FILE': 'q100viz/settings/buildings_interaction_grid_2.csv',
    'GRID_1_INPUT_SCENARIOS_FILE': 'q100viz/settings/buildings_interaction_grid_1.csv',
    'GRID_2_INPUT_SCENARIOS_FILE': 'q100viz/settings/buildings_interaction_grid_2.csv',
    'GRID_1_INDIVIDUAL_DATA_VIEW_FILE': 'q100viz/settings/individual_data_view_grid_1.csv',
    'GRID_2_INDIVIDUAL_DATA_VIEW_FILE': 'q100viz/settings/individual_data_view_grid_2.csv',
    'GRID_1_TOTAL_DATA_VIEW_FILE': 'q100viz/settings/total_data_view_grid_1.csv',
    'GRID_2_TOTAL_DATA_VIEW_FILE': 'q100viz/settings/total_data_view_grid_2.csv',

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
