import json
import pandas
import threading
import socketio
import q100viz.session as session
import datetime

class Stats:
    def __init__(self, socket_addr):
        # set up Socket.IO client to talk to stats viz
        self.io = socketio.Client()

        def run():
            self.io.connect(socket_addr)
            self.io.wait()

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

        self.previous_message = None

    def send_message(self, msg):
        if msg != self.previous_message:
            session.print_verbose(datetime.datetime.now().strftime(" %H:%M:%S ") + "sending data:\n" + str(msg))
            try:
                self.io.emit('message', msg)
                self.previous_message = msg
            except Exception:
                pass

    def send_max_values(self, max_values, min_values):
        self.send_message("init\n" + "\n".join(map(str, max_values + min_values)))

    def send_dataframe_as_json(self, df):
        self.send_message(export_json(df, None))

    def send_dataframe_with_environment_variables(self, df, env):
        data = json.loads(export_json(df, None))
        result = data[0] if len(data) > 0 else {}
        for key, value in env.items():
            result[key] = value
        self.send_message([json.dumps(result, ensure_ascii=False)])

    def send_simplified_dataframe_with_environment_variables(self, df, env):
        sum = make_clusters(df).sum()
        data = json.loads(export_json(sum, None))
        if len(data) > 0:
            result = data[0]
            for key, value in env.items():
                result[key] = value
            clusterData = json.loads(export_json(df[["address","CO2","connection_to_heat_grid","electricity_supplier","heat_consumption","electricity_consumption", "refurbished"]], None))
            result["clusters"] = clusterData
            self.send_message([json.dumps(result)])

    def send_dataframes_as_json(self, dfs):
        self.send_message(json.dumps([json.loads(export_json(df, None)) for df in dfs]))

def append_csv(file, df, cols):
    """Open data from CSV and join them with a GeoDataFrame based on osm_id."""
    values = pandas.read_csv(
        file, usecols=['osm_id', *cols.keys()], dtype=cols).set_index('osm_id')
    return df.join(values, on='osm_id')


def make_clusters(buildings):
    # group the buildings by cell ID
    return buildings.groupby(by='cell')


def export_json(df, outfile):
    """Export a dataframe to JSON file."""
    return pandas.DataFrame(df).to_json(
        outfile, orient='records', force_ascii=False, default_handler=str)

def to_xml(row):
    xml = ['<Experiment>']
    for field in row.index:
        xml.append('  <Parameter name="{0}">{1}</Parameter>'.format(field, row[field]))
    xml.append('</Experiment>')
    return '\n'.join(xml)