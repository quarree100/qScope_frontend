import pandas
import udp


class Stats:
    def __init__(self, udp_address, udp_port):
        # set up UDP client to talk to stats viz
        self.udp_client = udp.UDPClient(udp_address, udp_port)

    def send_max_values(self, max_values, min_values):
        init = "init\n" + "\n".join(map(str, max_values + min_values))
        self.udp_client.send_message(init)

    def append_csv(self, file, df, cols):
        """Open data from CSV and join them with a GeoDataFrame based on osm_id."""
        values = pandas.read_csv(file, usecols=['osm_id', *cols.keys()], dtype=cols).set_index('osm_id')

        return df.join(values, on='osm_id')
