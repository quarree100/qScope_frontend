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
    'GAMA_OUTPUT_FOLDER': '../data/headless/output',
    'GAMA_MODEL_FILE' : '../q100_abm/q100/models/qscope_ABM.gaml',

    # grid setup
    'CSPY_SETTINGS_FILE': '../cspy/settings/cityscopy.json',
    'GRID_1_SETUP_FILE': 'q100viz/settings/input_households_grid_1.csv',
    'GRID_2_SETUP_FILE': 'q100viz/settings/input_households_grid_2.csv',
    'GRID_1_INPUT_SCENARIOS_FILE': 'q100viz/settings/input_scenarios_grid_1.csv',
    'GRID_2_INPUT_SCENARIOS_FILE': 'q100viz/settings/input_scenarios_grid_2.csv',
    'GRID_1_DATA_VIEW_FILE': 'q100viz/settings/data_view_grid_1.csv',
    'GRID_2_DATA_VIEW_FILE': 'q100viz/settings/data_view_grid_2.csv',

    'GRID_2_X1' : 50,
    'GRID_2_X2' : 100,
    'GRID_2_Y1' : 0,
    'GRID_2_Y2' : 81.818,

    'GRID_1_X1' : 0,
    'GRID_1_X2' : 50,
    'GRID_1_Y1' : 0,
    'GRID_1_Y2' : 81.818
}
