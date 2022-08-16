import csv
from datetime import datetime
import pandas
import matplotlib.pyplot as plt

input = "date ('2020-01-03 00:00:00')"
print(input[7:-11])
dt_object = datetime.strptime(input[7:-11], '%Y-%m-%d')
print(dt_object)

def GAMA_time_to_datetime(input):
    dt_object = datetime.strptime(input[7:-11], '%Y-%m-%d')
    return(dt_object)

csv_data = (pandas.read_csv("/home/dunland/github/qScope/data/outputs/output/emissions/CO2_emissions_neighborhood.csv"))
print([(col, val) for col, val in csv_data.iteritems()])
csv_data['current_date'] = csv_data['current_date'].apply(GAMA_time_to_datetime)

with pandas.option_context('display.max_rows', None,
                    'display.max_columns', None,
                    'display.precision', 3,
                    ):
    print(csv_data)