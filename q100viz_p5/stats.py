import csv
import udp


class Stats:
    def __init__(self, udp_address, udp_port):
        # set up UDP client to talk to stats viz
        self.udp_client = udp.UDPClient(udp_address, udp_port)

    def send_max_values(self, max_values, min_values):
        init = "init\n" + "\n".join(map(str, max_values + min_values))
        self.udp_client.send_message(init)

    def read_csv(self, file, df, dtypes):
        """Open data from CSV and join them with a GeoDataFrame based on osm_id."""
        with open(file, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            for row in reader:
                try:
                    osm_id = int(row['osm_id'])
                except ValueError:
                    print("Failed to parse osm_id")
                    continue

                for key, dtype in dtypes.items():
                    if dtype in [int, 'int16', 'int32', 'int64']:
                        try:
                            df.loc[df['osm_id'] == osm_id, key] = int(row[key])
                        except ValueError:
                            print("Failed to parse int")
                    if dtype in [float, 'float32', 'float64']:
                        try:
                            df.loc[df['osm_id'] == osm_id, key] = float(row[key])
                        except ValueError:
                            print("Failed to parse float")
                    else:
                        df.loc[df['osm_id'] == osm_id, key] = row[key]

        try:
            df = df.astype(dtypes)
        except Exception:
            print("Failed to update data types")
