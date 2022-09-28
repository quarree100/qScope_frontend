import buildings as bd
import graphs

random_buildings = bd.random_buildings(bd.buildings_df, 100, True)
bdgl = bd.buildings_groups_list(random_buildings, bd.COMMUNICATION_RELEVANT_KEYS)
graphs.export_combined_emissions_graph(bdgl, '../../data/outputs/output_test', outfile=None, graph_popup=True)