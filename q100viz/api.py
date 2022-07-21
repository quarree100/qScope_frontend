import json
import pandas
import threading
import socketio
import q100viz.session as session
import datetime

class API:
    def __init__(self, socket_addr):
        # set up Socket.IO client to talk to stats viz
        self.io = socketio.Client()

        def run():
            self.io.connect(socket_addr)
            self.io.wait()

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

        self.previous_message = None
        self.timed_message_buffer_time = datetime.timedelta(milliseconds=250) # buffer time for timed messages
        self.last_timed_message_start = 0
        self.timed_message = None

    def send_message(self, msg):
        if msg != self.previous_message:
            session.print_verbose(datetime.datetime.now().strftime(" %H:%M:%S ") + "sending data:\n" + str(msg))
            try:
                self.io.emit('message', msg)
                self.previous_message = msg
            except Exception:
                pass

    # overwrite timed message:
    def setup_timed_message(self, msg, interval):
        self.timed_message_buffer_time = datetime.timedelta(milliseconds=interval)
        self.timed_message = msg
        session.flag_check_timed_messages = True
        self.last_timed_message_start = datetime.datetime.now()
        print("timed message set to send:", msg)

    # send timed message if no change:
    def send_timed_messages(self):
        if datetime.datetime.now() - self.last_timed_message_start > self.timed_message_buffer_time:
        # if msg != self.previous_message:
            session.print_verbose(datetime.datetime.now().strftime(" %H:%M:%S ") + "sending data:\n" + str(self.timed_message))
            try:
                self.io.emit('message', self.timed_message)
                self.previous_message = self.timed_message
            except Exception:
                pass

        session.flag_check_timed_messages = False

    def send_max_values(self, max_values, min_values):
        self.send_message("init\n" + "\n".join(map(str, max_values + min_values)))

    def send_dataframe_as_json(self, df):
        data = json.loads(export_json(df, None))
        result = data[0] if len(data) > 0 else {}
        self.send_message(json.dumps(result, ensure_ascii=False))

    def send_df_with_session_env(self, df):
        data = json.loads(export_json(df, None))
        result = data[0] if len(data) > 0 else {}
        for key, value in session.environment.items():
            result[key] = value
        self.send_message(json.dumps(result, ensure_ascii=False))

    def send_session_env(self):
        result = {}
        for key, value in session.environment.items():
            result[key] = value
        self.send_message(json.dumps(result, ensure_ascii=False))

    def send_dataframe_using_keys(self, df, keys):
        sum = make_clusters(df).sum()
        data = json.loads(export_json(sum, None))
        if len(data) > 0:
            result = data[0]
            clusterData = json.loads(export_json(df[keys], None))
            result["clusters"] = clusterData
            self.send_message(json.dumps(result))

    def send_grouped_buildings(self):

        bd = session.buildings

        session.buildings_groups = [
            bd[bd['group'] == 0][session.communication_relevant_keys],
            bd[bd['group'] == 1][session.communication_relevant_keys],
            bd[bd['group'] == 2][session.communication_relevant_keys],
            bd[bd['group'] == 3][session.communication_relevant_keys]]

        wrapper = ['' for i in range(session.num_of_users)]
        i = 0
        message = {}

        for group in session.buildings_groups:
            # aggregated data:
            connections_sum = make_clusters(group)['connection_to_heat_grid'].sum()
            data = json.loads(export_json(connections_sum.rename('connections', inplace=True), None))

            result = {}
            if len(data) > 0:
                result = data[0]
                groupData = json.loads(
                    export_json(group[session.communication_relevant_keys], None))
                result["buildings".format(str(i))] = groupData
                message['group_{0}'.format(str(i))] = result
            else:  # create empty elements for empty groups (infoscreen reset)
                message['group_{0}'.format(str(i))] = ['']

            wrapper = {
                'buildings_groups' : message
            }

            self.setup_timed_message(json.dumps(wrapper), 0)

            i += 1

    def send_simplified_dataframe_with_environment_variables(self, df, env):
        sum = make_clusters(df).sum()
        data = json.loads(export_json(sum, None))
        if len(data) > 0:
            result = data[0]
            for key, value in env.items():
                result[key] = value
            clusterData = json.loads(export_json(df[["address","CO2","connection_to_heat_grid", "refurbished", "environmental_engagement"]], None))
            result["clusters"] = clusterData
            self.send_message(json.dumps(result))

    def send_dataframe(self, dfs):
        self.send_message(json.dumps([json.loads(export_json(df, None)) for df in dfs]))

def append_csv(file, df, cols):
    """Open data from CSV and join them with a GeoDataFrame based on osm_id."""
    values = pandas.read_csv(
        file, usecols=['osm_id', *cols.keys()], dtype=cols, error_bad_lines=False, delimiter=';').set_index('osm_id')
    return df.join(values, on='osm_id')


def make_clusters(buildings):
    # group the buildings by cell ID
    return buildings.groupby(by='cell')


def export_json(df, outfile):
    """Export a dataframe to JSON file."""
    return pandas.DataFrame(df).to_json(
        outfile, orient='records', force_ascii=False, default_handler=str)

def print_full_df(df):
    with pandas.option_context('display.max_rows', None,
                        'display.max_columns', None,
                        'display.precision', 3,
                        ):
        print(df)