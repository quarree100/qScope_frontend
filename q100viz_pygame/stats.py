import json
import pandas

import udp


class Stats:
    def __init__(self, udp_address, udp_port):
        # set up UDP client to talk to stats viz
        self.udp_client = udp.UDPClient(udp_address, udp_port)

    def send_max_values(self, max_values, min_values):
        init = "init\n" + "\n".join(map(str, max_values + min_values))
        self.udp_client.send_message(init)

    def send_dataframe_as_json(self, df):
        self.udp_client.send_message(export_json(df, None))

    def send_dataframes_as_json(self, dfs):
        msg = json.dumps([json.loads(export_json(df, None)) for df in dfs])
        self.udp_client.send_message(msg)


def append_csv(file, df, cols):
    """Open data from CSV and join them with a GeoDataFrame based on osm_id."""
    values = pandas.read_csv(file, usecols=['osm_id', *cols.keys()], dtype=cols).set_index('osm_id')
    return df.join(values, on='osm_id')


def make_clusters(buildings):
    # group the buildings by cell ID
    return buildings.groupby(by='cell')


def export_json(df, outfile):
    """Export a dataframe to JSON file."""
    return pandas.DataFrame(df).to_json(outfile, orient='records', force_ascii=False, default_handler=str)
