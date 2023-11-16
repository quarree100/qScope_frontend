import json
import pandas
import threading
import socketio
import q100viz.session as session
from q100viz.devtools import devtools
import datetime
from q100viz.settings.config import config

class API:
    def __init__(self, socket_addr):
        # set up Socket.IO client to talk to stats viz
        self.io = socketio.Client()

        def run():
            try:
                self.io.connect(socket_addr)
                self.io.wait()
            except:
                print("---Warning: cannot connect to localhost:" + str(config['UDP_SERVER_PORT']) + ". Did you start the infoscreen?")

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

        self.previous_message = None

    def send_message(self, msg):
        '''simple function to finally send a message via UDP. It should have json format for the infoscreen to process it properly.'''
        if msg != self.previous_message:
            devtools.print_verbose(datetime.datetime.now().strftime(
                " %H:%M:%S ") + "sending data:\n" + str(msg))
            try:
                self.io.emit('message', msg)
                self.previous_message = msg
            except Exception:
                pass

    def send_dataframe_as_json(self, df):
        '''make a json struct from a pandas DataFrame object and send it via send_message()'''
        data = json.loads(export_json(df, None))
        result = data[0] if len(data) > 0 else {}
        self.send_message(json.dumps(result, ensure_ascii=False))

    def send_df_with_session_env(self, df):
        '''translates a pandas DataFrame to json format and appends the session.environment dict'''
        data = json.loads(export_json(df, None))
        result = data[0] if len(data) > 0 else {}
        for key, value in session.environment.items():
            result[key] = value
        self.send_message(json.dumps(result, ensure_ascii=False))

    def send_session_env(self):
        '''simply send the session.environment dict as json format'''
        result = {}
        for key, value in session.environment.items():
            result[key] = value
        self.send_message(json.dumps(result, ensure_ascii=False))

    def forward_gama_message(self, msg):
        '''formats gama simulation status message to percentage and forwards it to the infoscreen via send_message()'''
        msg = msg.replace("'", "\"")
        json_object = json.loads(msg)
        session.simulation.progress = "{0}%".format(int(0.5 + json_object['step'] / session.simulation.final_step * 100))
        self.send_message(json.dumps(json.loads(msg)))

def append_csv(file, df, cols):
    """Open data from CSV and join them with a GeoDataFrame based on osm_id."""
    values = pandas.read_csv(
        file, usecols=['osm_id', *cols.keys()], dtype=cols, error_bad_lines=False, delimiter=';').set_index('osm_id')
    return df.join(values, on='osm_id')

def export_json(df, outfile=None):
    """Export a dataframe to JSON file. This is necessary to transform GeoDataFrames into a JSON serializable format"""
    return pandas.DataFrame(df).to_json(
        outfile, orient='records', force_ascii=False, default_handler=str)
