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

    def send_message(self, msg):
        if msg != self.previous_message:
            session.print_verbose(datetime.datetime.now().strftime(
                " %H:%M:%S ") + "sending data:\n" + str(msg))
            try:
                self.io.emit('message', msg)
                self.previous_message = msg
            except Exception:
                pass

    def send_max_values(self, max_values, min_values):
        self.send_message(
            "init\n" + "\n".join(map(str, max_values + min_values)))

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
        sum = df.groupby(by='cell').sum()
        data = json.loads(export_json(sum, None))
        if len(data) > 0:
            result = data[0]
            clusterData = json.loads(export_json(df[keys], None))
            result["clusters"] = clusterData
            self.send_message(json.dumps(result))

    def make_buildings_groups_json(self):
        '''compose a json struct for selected buildings if each user can handle multiple buildings'''

        bd = session.buildings

        session.buildings_groups = [
            bd[bd['group'] == 0][session.COMMUNICATION_RELEVANT_KEYS],
            bd[bd['group'] == 1][session.COMMUNICATION_RELEVANT_KEYS],
            bd[bd['group'] == 2][session.COMMUNICATION_RELEVANT_KEYS],
            bd[bd['group'] == 3][session.COMMUNICATION_RELEVANT_KEYS]]

        wrapper = ['' for i in range(session.num_of_users)]
        i = 0
        message = {}

        for group in session.buildings_groups:
            print("group:", group)
            # aggregated data:
            # connections_sum = group.groupby(
            #     by='cell')['connection_to_heat_grid'].sum()
            # print("connections_sum:", connections_sum)
            # data = json.loads(export_json(
            #     connections_sum.rename('connections', inplace=True), None))
            # print("data:", data)

            group_wrapper = {}
            if len(group) > 0:
                # group_data = data[0]
                user_selected_buildings = json.loads(
                    export_json(group[session.COMMUNICATION_RELEVANT_KEYS], None))
                group_wrapper['buildings'] = user_selected_buildings
                print("group_wrapper:", group_wrapper)

                # get all buildings with similar stats
                buildings_cluster = make_clusters(group)
                # get average building from this:
                average_generic_buildings = []
                for idx, average_building in enumerate(buildings_cluster):
                    average_building = pandas.DataFrame()
                    for key in ['spec_heat_consumption', 'spec_power_consumption']:
                        average_building[key] = [
                            buildings_cluster[idx][key].mean()]
                    average_building['address'] = group.loc[group.index[idx],'address']
                    average_generic_buildings.append(json.loads(export_json(average_building)))

                group_wrapper['average_generic_buildings'] = average_generic_buildings

                # make JSON serializable object from GeoDataFrame
                # group_data['clusters'] = json.loads(
                # export_json(buildings_cluster))
                message['group_{0}'.format(str(i))] = group_wrapper
            else:  # create empty elements for empty groups (infoscreen reset)
                message['group_{0}'.format(str(i))] = ['']

            wrapper = {
                'buildings_groups': message
            }

            i += 1

        return wrapper

    def send_simplified_dataframe_with_environment_variables(self, df, env):
        sum = df.groupby(by='cell').sum()
        data = json.loads(export_json(sum, None))
        if len(data) > 0:
            result = data[0]
            for key, value in env.items():
                result[key] = value
            clusterData = json.loads(export_json(
                df[["address", "CO2", "connection_to_heat_grid", "refurbished", "environmental_engagement"]], None))
            result["clusters"] = clusterData
            self.send_message(json.dumps(result))

    def send_dataframe(self, dfs):
        self.send_message(json.dumps(
            [json.loads(export_json(df, None)) for df in dfs]))


def append_csv(file, df, cols):
    """Open data from CSV and join them with a GeoDataFrame based on osm_id."""
    values = pandas.read_csv(
        file, usecols=['osm_id', *cols.keys()], dtype=cols, error_bad_lines=False, delimiter=';').set_index('osm_id')
    return df.join(values, on='osm_id')


def make_clusters(group):
    '''make groups from one (!!) selected building. always only returns a cluster of the first building in group!'''
    cluster = []
    for idx in range(len(group.index)):
        cluster.append(
            session.buildings.loc[(
                # (session.buildings['energy_source'] == group.loc[
                #     group.index[idx], 'energy_source'])
                # &
                (session.buildings['spec_heat_consumption'] >= session.buildings.loc[session.buildings.index[idx],
                 'spec_heat_consumption'] - session.buildings['spec_heat_consumption'].std()/2)
                &
                (session.buildings['spec_heat_consumption'] <= session.buildings.loc[session.buildings.index[idx],
                 'spec_heat_consumption'] + session.buildings['spec_heat_consumption'].std()/2)
                &
                (session.buildings['spec_power_consumption'] >= session.buildings.loc[session.buildings.index[idx],
                 'spec_power_consumption'] - session.buildings['spec_power_consumption'].std()/2)
                &
                (session.buildings['spec_power_consumption'] <= session.buildings.loc[session.buildings.index[idx],
                 'spec_power_consumption'] + session.buildings['spec_power_consumption'].std()/2)
            )]
        )
        session.print_verbose("building {0} is linked to {1} other buildings with similar specs:\n{2}".format(
            group.index[idx], len(cluster[idx]), cluster[idx][['spec_heat_consumption', 'spec_power_consumption']].describe()))
    return cluster


def export_json(df, outfile=None):
    """Export a dataframe to JSON file. This is necessary to transform GeoDataFrames into a JSON serializable format"""
    return pandas.DataFrame(df).to_json(
        outfile, orient='records', force_ascii=False, default_handler=str)


def print_full_df(df):
    with pandas.option_context('display.max_rows', None,
                               'display.max_columns', None,
                               'display.precision', 3,
                               ):
        print(df)
