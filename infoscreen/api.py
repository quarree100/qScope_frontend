import time
import json
import pandas
import numpy as np
import threading
import socketio
from q100viz.devtools import devtools
import datetime
from q100viz.settings.config import config
import q100viz.session as session

class API:
    def __init__(self, socket_addr):
        # set up Socket.IO client to talk to stats viz
        self.io = socketio.Client()
        self.connected = False
           
        def run():
            try:
                self.io.connect(socket_addr, wait=True, retry=True)
                self.connected = True
                self.start_emit_thread()
                self.io.wait()
            except Exception as e:
                print(f"---Warning: cannot connect to localhost:{socket_addr}. \n{e}\n(Did you start the infoscreen?)")

        connection_thread = threading.Thread(target=run, daemon=True)
        connection_thread.start()
                    
        self.previous_message = None
        self.message_stack = []
        
    def start_emit_thread(self):
        '''Startet den Thread für das regelmäßige Versenden von Nachrichten.'''
        def emit_worker():
            while self.connected:
                if self.message_stack:
                    self.emit_messages()
                time.sleep(1)

        emit_thread = threading.Thread(target=emit_worker, daemon=True)
        emit_thread.start()        
        
    def emit_messages(self):
        '''flushes the message stack and sends all via UDP.
        This function will be used to throttle messages flush to 1/s'''
        for message in list(self.message_stack):
            self.send_message(message)
            self.message_stack.remove(message)
            
    def push_message(self, json_string):
        if json_string != self.previous_message:
            self.message_stack.append(json_string)
            self.previous_message = json_string

    def send_message(self, msg):
        '''simple function to finally send a message via UDP. It should have json format for the infoscreen to process it properly.'''
        devtools.print_verbose(datetime.datetime.now().strftime(
            " %H:%M:%S ") + "sending data:\n" + str(msg))
        try:
            self.io.emit('message', msg)
        except Exception:
            pass
            
    def send_message_as_json(self, message):
        self.push_message(json.dumps(message))

    def send_dataframe_as_json(self, df):
        '''make a json struct from a pandas DataFrame object and send it via send_message()'''
        data = json.loads(export_json(df, None))
        result = data[0] if len(data) > 0 else {}
        self.push_message(json.dumps(result, ensure_ascii=False))

    def send_df_with_session_env(self, df, env):
        '''translates a pandas DataFrame to json format and appends the session.environment dict'''
        data = json.loads(export_json(df, None))
        result = data[0] if len(data) > 0 else {}
        for key, value in env.items():
            result[key] = value
        self.push_message(json.dumps(result, ensure_ascii=False))

    def send_dict(self, dict):
        '''convert dict to json format and send'''
        result = {}
        for key, value in dict.items():
            if isinstance(value, np.integer):
                result[key] = int(value)
            else:
                result[key] = value
        self.push_message(json.dumps(result, ensure_ascii=False))
                
def append_csv(file, df, cols):
    """Open data from CSV and join them with a GeoDataFrame based on osm_id."""
    values = pandas.read_csv(
        file, usecols=['osm_id', *cols.keys()], dtype=cols, error_bad_lines=False, delimiter=';').set_index('osm_id')
    return df.join(values, on='osm_id')

def export_json(df, outfile=None):
    """Export a dataframe to JSON file. This is necessary to transform GeoDataFrames into a JSON serializable format"""
    return pandas.DataFrame(df).to_json(
        outfile, orient='records', force_ascii=False, default_handler=str)

def forward_gama_message(msg):
    '''formats gama simulation status message to percentage and forwards it to the infoscreen via send_message()'''
    if not session.modes['simulation'].running: return
    print("receive", msg)
    msg = msg.replace("'", "\"")
    json_object = json.loads(msg)
    session.modes['simulation'].progress = f"{int(0.5 + json_object['step'] / session.modes['simulation'].final_step * 100)}%"
    session.api.push_message(json.dumps(json.loads(msg)))